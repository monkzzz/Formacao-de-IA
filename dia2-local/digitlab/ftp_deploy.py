"""Deploy static assets using an ignored local configuration; never log secrets."""

import argparse
import ftplib
import hashlib
import io
import json
import posixpath
import re
import socket
import ssl
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from uuid import uuid4

from .qa_outputs import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def deployment_order(path):
    """Transfer shared runtimes before their entry modules, and HTML last."""
    relative = path.relative_to(ROOT / "dist").as_posix()
    priority = {"preprocess.js": 1, "words.js": 1, "inference.js": 2,
                "digit-readers.js": 2, "helper.js": 2, "app.js": 3}
    return (relative == "index.html", priority.get(path.name, 0), relative)


def connect(config):
    host = config.get("tls_hostname") or config["host"]
    if host != config["host"]:
        original = {r[4][0] for r in socket.getaddrinfo(config["host"], None)}
        canonical = {r[4][0] for r in socket.getaddrinfo(host, None)}
        if not original.intersection(canonical):
            raise ValueError("TLS hostname must resolve to the same server as the configured FTP host")
    client = ftplib.FTP_TLS(context=ssl.create_default_context()) if config.get("tls", True) else ftplib.FTP()
    client.connect(host, int(config.get("port", 21)), timeout=30)
    client.login(config["username"], config["password"])
    if config.get("tls", True):
        client.prot_p()
    client.set_pasv(True)
    return client


def listing(client):
    try:
        return [{"name": name, "type": facts.get("type"), "size": facts.get("size")}
                for name, facts in client.mlsd() if name not in [".", ".."]]
    except ftplib.error_perm:
        return [{"name": name} for name in client.nlst()]


def enter_directory(client, directory, create=False, allow_root=False):
    if directory in [".", "/"] and allow_root:
        if directory == "/":
            client.cwd("/")
        return client.pwd()
    if not directory or directory in [".", "/"]:
        raise ValueError("Set a specific remote_dir for the app before deployment")
    if ".." in directory.split("/"):
        raise ValueError("Parent traversal is not permitted in remote_dir")
    if directory.startswith("/"):
        client.cwd("/")
    for part in directory.split("/"):
        if not part or part == ".":
            continue
        try:
            client.cwd(part)
        except ftplib.error_perm:
            if not create:
                raise
            client.mkd(part)
            client.cwd(part)
    return client.pwd()


def deployment_files(manifest=None, selected=None):
    manifest = Path(manifest) if manifest is not None else ROOT / "deployment-files.json"
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    names = metadata["files"]
    if metadata.get("schema") != 1 or not names or len(names) != len(set(names)):
        raise ValueError("Require a nonempty, unique reviewed deployment allowlist")
    files = []
    suffixes = {".html", ".js", ".mjs", ".css", ".json", ".bin", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico", ".woff", ".woff2", ".ttf"}
    for name in names:
        relative = PurePosixPath(name)
        path = ROOT / "dist" / name
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name
                or any(part.startswith(".") for part in relative.parts)
                or relative.as_posix() != name or relative.suffix.lower() not in suffixes
                or relative.name in ("parity.json", "ftp.local.json")
                or (relative.suffix.lower() == ".bin" and (relative.parts[0] != "model" or relative.name != "weights.bin"))
                or not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to((ROOT / "dist").resolve())):
            raise ValueError("Unsafe or missing deployment allowlist entry: " + name)
        files.append(path)
    if selected is not None:
        if not selected or not set(selected) <= set(names):
            raise ValueError("Selected files must be in the reviewed deployment allowlist")
        files = [p for p in files if p.relative_to(ROOT / "dist").as_posix() in selected]
    return sorted(files, key=deployment_order)


def upload_file(client, path, backup, report, persist):
    """Verify a unique temporary remote file before publishing it with RNFR/RNTO."""
    relative = path.relative_to(ROOT / "dist").as_posix()
    payload = path.read_bytes()
    checksum = hashlib.sha256(payload).hexdigest()
    name = path.name
    temporary = "." + name + ".upload-" + uuid4().hex
    current = {"file": relative, "bytes": len(payload), "sha256": checksum,
               "phase": "BACKUP", "temporary_remote_file": temporary}
    report["current_file"] = current
    persist()
    previous = io.BytesIO()
    try:
        client.retrbinary("RETR " + name, previous.write)
    except ftplib.error_perm as error:
        if not str(error).startswith("550"):
            raise
        # 550 can also mean permission denied: never treat a visible file as absent.
        if name in {posixpath.basename(item) for item in client.nlst()}:
            raise
        current["previous_file"] = "ABSENT"
    else:
        saved = backup / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(previous.getvalue())
        current["previous_sha256"] = hashlib.sha256(previous.getvalue()).hexdigest()
    try:
        current["phase"] = "UPLOADING_TEMPORARY"
        persist()
        client.storbinary("STOR " + temporary, io.BytesIO(payload))
        received = io.BytesIO()
        client.retrbinary("RETR " + temporary, received.write)
        if hashlib.sha256(received.getvalue()).hexdigest() != checksum:
            raise RuntimeError("Temporary uploaded asset integrity check failed")
        current["phase"] = "PUBLISHING_VERIFIED_TEMPORARY"
        persist()
        # Refuse unsupported replacement rather than deleting a working remote file.
        client.rename(temporary, name)
        current["phase"] = "PUBLISHED; VERIFYING"
        persist()
        received = io.BytesIO()
        client.retrbinary("RETR " + name, received.write)
        if hashlib.sha256(received.getvalue()).hexdigest() != checksum:
            raise RuntimeError("Published asset integrity check failed")
        current["phase"] = "PUBLISHED_AND_VERIFIED"
        report["files"].append({"file": relative, "bytes": len(payload), "sha256": checksum})
        persist()
    except BaseException:
        try:
            client.delete(temporary)
            current["temporary_cleanup"] = "REMOVED"
        except Exception:
            current["temporary_cleanup"] = "NOT CONFIRMED; inspect remote temporary file"
        persist()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--report", default="ftp-deployment.json")
    parser.add_argument("--files", nargs="+", help="Reviewed relative dist paths, dependencies before index.html")
    parser.add_argument("--manifest", type=Path, default=ROOT / "deployment-files.json")
    args = parser.parse_args()
    report_path = ROOT / "reports" / args.report
    if args.upload and report_path.exists():
        raise FileExistsError("Preserve existing deployment evidence; use a new --report")
    files = deployment_files(args.manifest, args.files) if args.upload else []
    client, report = None, None
    if args.upload:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
                  "files": [], "plan": [p.relative_to(ROOT / "dist").as_posix() for p in files],
                  "scope": "Reviewed allowlist; per-file staged publication, not an atomic whole-site switch"}
        with report_path.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
    def persist():
        atomic_json(report_path, report)
    try:
        config = json.loads((ROOT / "ftp.local.json").read_text(encoding="utf-8-sig"))
        if not all(config.get(key) for key in ("host", "username", "password")):
            raise ValueError("Missing deployment credentials")
        client = connect(config)
        target = enter_directory(client, config.get("remote_dir", ""), create=args.upload,
                                 allow_root=config.get("allow_ftp_root", False))
        if not args.upload:
            print(json.dumps({"connected": True, "tls": config.get("tls", True), "destination": target,
                              "entries": listing(client)}), flush=True)
            return
        backup = ROOT / "artifacts" / ("ftp-backup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8])
        backup.mkdir(parents=True, exist_ok=False)
        report.update(destination=target, tls=config.get("tls", True), backup_directory=str(backup.relative_to(ROOT)),
                      manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest())
        persist()
        for path in files:
            client.cwd(target)
            parent = posixpath.dirname(path.relative_to(ROOT / "dist").as_posix())
            if parent:
                enter_directory(client, parent, create=True)
            upload_file(client, path, backup, report, persist)
            print(json.dumps({"verified_upload": report["files"][-1]["file"]}), flush=True)
        report.update(status="PASS", completed_utc=datetime.now(timezone.utc).isoformat())
        persist()
    except BaseException as error:
        # FTP messages can echo authentication data; retain category/code only.
        code = str(error)[:3] if isinstance(error, ftplib.Error) else ""
        failure = {"error_type": type(error).__name__, "ftp_code": code if code.isdigit() else ""}
        if report is not None:
            report.update(status="FAIL", failure=failure)
            persist()
        print(json.dumps({"status": "FAIL", **failure}), flush=True)
        raise SystemExit(1) from None
    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                client.close()


if __name__ == "__main__":
    main()
