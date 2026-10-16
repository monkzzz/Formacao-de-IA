"""Read-only hosting diagnostics; no credentials or website changes."""

import json
import urllib.error
import urllib.request


def main():
    paths = ["index.html", "app.js", "inference.js", "preprocess.js", "style.css",
             "model/manifest.json", "model/weights.bin"]
    for scheme in ["http", "https"]:
        for path in paths:
            url = f"{scheme}://naoquerosaber.pt/AI/{path}"
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "DigitLab-Hosting-Check/1.0"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    body = response.read()
                    result = {"url": url, "status": response.status,
                              "final_url": response.url, "content_type": response.headers.get("Content-Type"),
                              "bytes": len(body)}
                    if path in ["index.html", "model/manifest.json"]:
                        result["preview"] = body[:200].decode("utf-8", errors="replace")
                    print(json.dumps(result), flush=True)
            except Exception as error:
                print(json.dumps({"url": url, "error": str(error)}), flush=True)


if __name__ == "__main__":
    main()
