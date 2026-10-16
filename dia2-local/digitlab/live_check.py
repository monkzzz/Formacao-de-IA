"""Observe the public page in a normal browser without changing the website."""

import json
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


def main():
    observations = []
    with sync_playwright() as p:
        browser = open_browser(p)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        for url in ["https://naoquerosaber.pt/AI/index.html",
                    "https://naoquerosaber.pt/AI/index.html?digitlab_check=" + str(time.time_ns())]:
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as error:
                observations.append({"url": url, "ready": False, "navigation_error": str(error)})
                continue
            for attempt in range(5):
                page.wait_for_timeout(3000)
                ready = page.evaluate("!!window.digitLab?.state.ready")
                observation = {"url": page.url, "initial_status": response.status,
                               "title": page.title(), "ready": ready,
                               "body_preview": page.locator("body").inner_text()[:500]}
                observations.append(observation)
                print(json.dumps(observation), flush=True)
                if ready or "404" in page.title():
                    break
            if observations[-1]["ready"]:
                break
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        try:
            page.screenshot(path=str(screenshots / "live-hosting.png"), full_page=True)
        except Exception as error:
            errors.append(str(error))
        browser.close()
    write_json(ROOT / "reports/live-hosting-check.json",
               {"checked_at": datetime.now(timezone.utc).isoformat(), "observations": observations, "page_errors": errors})


if __name__ == "__main__":
    main()
