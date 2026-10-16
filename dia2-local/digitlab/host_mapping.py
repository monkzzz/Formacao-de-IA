"""Probe likely public paths to identify an FTP account's document root."""

import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def probe(path):
    url = "https://naoquerosaber.pt" + path + "?digitlab_check=" + str(time.time_ns())
    try:
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read()
            return {"url": url, "status": response.status, "bytes": len(data),
                    "matches_app_index": hashlib.sha256(data).digest() == hashlib.sha256((ROOT / "dist/index.html").read_bytes()).digest()}
    except urllib.error.HTTPError as error:
        return {"url": url, "status": error.code,
                "headers": dict(error.headers), "preview": error.read(350).decode(errors="replace")}
    except Exception as error:
        return {"url": url, "error": str(error)}


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(probe, ["/AI/AI/index.html", "/AI/index.html", "/AI/", "/ai/index.html", "/index.html"]):
            print(json.dumps(result), flush=True)
