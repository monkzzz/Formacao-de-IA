"""Serve only static app assets on loopback; no inference or upload endpoint."""

import argparse
import hashlib
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen


def prepare_models(root, download=False):
    """Check current release weights; optionally restore verified public copies."""
    missing = []
    for relative in ("model", "model/captcha-v3/digits", "model/robust/letters"):
        folder = root / relative
        mode = "letters" if relative.endswith("letters") else "digits"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        target = folder / "weights.bin"
        if target.exists():
            continue
        if not download:
            missing.append(str(target.relative_to(root)))
            continue
        url = f"https://naoquerosaber.pt/AI/{relative}/weights.bin"
        print(f"Downloading {mode} weights...", flush=True)
        with urlopen(url, timeout=60) as response:
            data = response.read(manifest["bytes"] + 1)
        if len(data) != manifest["bytes"] or hashlib.sha256(data).hexdigest() != manifest["sha256"]:
            raise ValueError(f"Downloaded {mode} weights do not match the repository manifest.")
        temporary = target.with_suffix(".bin.part")
        temporary.write_bytes(data)
        temporary.replace(target)
        print(f"Verified {mode} weights.", flush=True)
    if missing:
        print("Missing trained models: " + ", ".join(missing), flush=True)
        print("Run: python serve.py --download-models", flush=True)
    supplementary = root / "model/mnist-supplementary-v1/digits"
    if (supplementary / "manifest.json").exists() and not (supplementary / "weights.bin").exists():
        print("Missing optional supplementary weights. Restore the matching local artifact, or follow docs/selectable-models.md to reproduce training; this model is not downloaded from the public release.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--download-models", action="store_true",
                        help="Download missing release weights and verify their SHA-256 hashes")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent / "dist"
    prepare_models(root, args.download_models)

    class Handler(SimpleHTTPRequestHandler):
        extensions_map = {
            **SimpleHTTPRequestHandler.extensions_map,
            ".js": "text/javascript",
            ".css": "text/css",
        }

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            super().end_headers()

    handler = partial(Handler, directory=str(root))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Digit Lab: http://127.0.0.1:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
