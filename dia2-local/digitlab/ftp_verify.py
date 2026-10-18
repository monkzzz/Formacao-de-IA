"""Read-only comparison between the FTP assets and the local application."""

import hashlib
import io
import json

from .ftp_deploy import ROOT, connect, deployment_files, enter_directory


def main():
    config = json.loads((ROOT / "ftp.local.json").read_text(encoding="utf-8"))
    client = connect(config)
    try:
        target = enter_directory(client, config["remote_dir"], allow_root=config.get("allow_ftp_root", False))
        results = []
        for path in deployment_files():
            relative = path.relative_to(ROOT / "dist").as_posix()
            remote = io.BytesIO()
            client.retrbinary("RETR " + relative, remote.write)
            results.append({"file": relative, "bytes": len(remote.getvalue()),
                            "matches_local": hashlib.sha256(remote.getvalue()).digest() == hashlib.sha256(path.read_bytes()).digest()})
        print(json.dumps({"ftp_directory": target, "files": results}, indent=2), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    main()
