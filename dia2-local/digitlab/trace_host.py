"""Record public navigation and asset responses to diagnose hosting redirects."""

import json
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


def main():
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "events": [], "snapshots": []}
    with sync_playwright() as p:
        browser = open_browser(p)
        context = browser.new_context(viewport={"width": 1280, "height": 960})
        page = context.new_page()

        def emit(event):
            event["at"] = round(time.monotonic(), 3)
            report["events"].append(event)
            print(json.dumps(event), flush=True)

        def response_event(response):
            if urlsplit(response.url).hostname not in ["naoquerosaber.pt", "www.naoquerosaber.pt"]:
                return
            headers = response.headers
            emit({"type": "response", "url": response.url, "status": response.status,
                  "resource": response.request.resource_type, "server": headers.get("server"),
                  "content_type": headers.get("content-type"), "location": headers.get("location")})

        page.on("response", response_event)
        page.on("framenavigated", lambda frame: emit({"type": "navigation", "url": frame.url}) if frame == page.main_frame else None)
        page.on("pageerror", lambda error: emit({"type": "script_error", "message": str(error)}))
        page.on("requestfailed", lambda request: emit({"type": "request_failed", "url": request.url, "failure": request.failure}))
        for url in ["http://naoquerosaber.pt/AI/index.html", "https://naoquerosaber.pt/AI/index.html"]:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                for attempt in range(6):
                    page.wait_for_timeout(2500)
                    observation = {"requested_url": url, "url": page.url, "title": page.title(),
                                   "body": page.locator("body").inner_text()[:650],
                                   "app_ready": page.evaluate("!!window.digitLab?.state.ready")}
                    report["snapshots"].append(observation)
                    print(json.dumps(observation), flush=True)
            except Exception as error:
                emit({"type": "observation_error", "url": url, "message": str(error)})
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        try:
            page.screenshot(path=str(screenshots / "hosting-trace.png"), full_page=True)
        except Exception:
            pass
        browser.close()
    write_json(ROOT / "reports/hosting-trace.json", report)


if __name__ == "__main__":
    main()
