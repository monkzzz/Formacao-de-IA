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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def deployment_order(path):
    """Transfer shared runtimes before their entry modules, and HTML last."""
    relative = path.relative_to(ROOT / "dist").as_posix()
    priority = {"preprocess.js": 1, "inference.js": 2, "helper.js": 2, "app.js": 3}
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--report", default="ftp-deployment.json",
                        help="Deployment report filename under reports")
    parser.add_argument("--files", nargs="+", help="Upload only these relative dist paths, dependencies before index.html")
    args = parser.parse_args()
    config = json.loads((ROOT / "ftp.local.json").read_text(encoding="utf-8-sig"))
    if not all(config.get(key) for key in ["host", "username", "password"]):
        raise SystemExit("Fill in host, username and password in ftp.local.json")
    client = None
    try:
        client = connect(config)
        home = client.pwd()
        print(json.dumps({"connected": True, "tls": config.get("tls", True),
                          "login_directory": home, "entries": listing(client)}), flush=True)
        destination = config.get("remote_dir", "")
        if not destination:
            print("Connection checked. Set remote_dir after identifying the website root.")
            return
        if not args.upload:
            try:
                target = enter_directory(client, destination, allow_root=config.get("allow_ftp_root", False))
                print(json.dumps({"destination": target, "entries": listing(client)}), flush=True)
            except ftplib.error_perm:
                print(json.dumps({"destination": destination, "status": "not accessible or not yet created"}), flush=True)
            return
        target = enter_directory(client, destination, create=True, allow_root=config.get("allow_ftp_root", False))
        # Upload versioned dependencies and model assets before switching the entry page.
        # Original root assets remain compatible with an already cached v1 page.
        files = sorted((path for path in (ROOT / "dist").rglob("*") if path.is_file() and path.name != "parity.json"),
                       key=deployment_order)
        if args.files:
            selected = set(args.files)
            known = {path.relative_to(ROOT / "dist").as_posix() for path in files}
            if not selected <= known:
                raise ValueError("Requested files must be existing relative static asset paths")
            files = [path for path in files if path.relative_to(ROOT / "dist").as_posix() in selected]
        # Existing remote files are downloaded before replacement; no remote files are deleted.
        backup = ROOT / "artifacts" / ("ftp-backup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        backup.mkdir(parents=True, exist_ok=False)
        uploaded = []
        for path in files:
            relative = path.relative_to(ROOT / "dist").as_posix()
            client.cwd(target)
            parent = posixpath.dirname(relative)
            if parent:
                enter_directory(client, parent, create=True)
            name = posixpath.basename(relative)
            old = io.BytesIO()
            try:
                client.retrbinary("RETR " + name, old.write)
            except ftplib.error_perm as error:
                if not str(error).startswith("550"):
                    raise
            else:
                previous = backup / relative
                previous.parent.mkdir(parents=True, exist_ok=True)
                previous.write_bytes(old.getvalue())
            with path.open("rb") as source:
                client.storbinary("STOR " + name, source)
            verify = io.BytesIO()
            client.retrbinary("RETR " + name, verify.write)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if hashlib.sha256(verify.getvalue()).hexdigest() != digest:
                raise RuntimeError("Uploaded asset integrity check failed")
            uploaded.append({"file": relative, "bytes": path.stat().st_size, "sha256": digest})
            print(json.dumps({"verified_upload": relative, "bytes": path.stat().st_size}), flush=True)
        report = {"uploaded_at": datetime.now(timezone.utc).isoformat(), "destination": target,
                  "tls": config.get("tls", True), "files": uploaded,
                  "backup_directory": str(backup.relative_to(ROOT))}
        version = re.search(r'id="app-version"[^>]*>v([^<]+)',
                            (ROOT / "dist/index.html").read_text(encoding="utf-8"))
        report["application_version"] = version.group(1) if version else None
        report["scope"] = "selected-files" if args.files else "all-static-assets"
        (ROOT / "reports" / args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    except Exception as error:
        # Server text can echo authentication data; print only its category/code.
        code = str(error)[:3] if isinstance(error, ftplib.Error) else ""
        print(json.dumps({"status": "failed", "error_type": type(error).__name__, "ftp_code": code}), flush=True)
        if isinstance(error, ssl.SSLCertVerificationError):
            print(json.dumps({"certificate_verification_code": error.verify_code,
                              "certificate_verification_message": error.verify_message}), flush=True)
        raise SystemExit(1)
    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                client.close()


if __name__ == "__main__":
    main()
