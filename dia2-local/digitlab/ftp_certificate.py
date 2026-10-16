"""Inspect the public FTP TLS certificate without authenticating."""

import ftplib
import json
import ssl
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = json.loads((ROOT / "ftp.local.json").read_text(encoding="utf-8-sig"))
    # Unverified TLS is used ONLY to retrieve the public certificate. Never login.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client = ftplib.FTP_TLS(context=context)
    try:
        client.connect(config["host"], int(config.get("port", 21)), timeout=20)
        client.auth()
        der = client.sock.getpeercert(binary_form=True)
        output = ROOT / "artifacts/ftp-public-certificate.pem"
        output.write_text(ssl.DER_cert_to_PEM_cert(der), encoding="ascii")
        decoded = ssl._ssl._test_decode_cert(str(output))
        print(json.dumps({"authenticated": False, "subject": decoded.get("subject"),
                          "issuer": decoded.get("issuer"), "not_before": decoded.get("notBefore"),
                          "not_after": decoded.get("notAfter"), "subject_alt_names": decoded.get("subjectAltName")}), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    main()
