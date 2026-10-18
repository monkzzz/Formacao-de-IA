"""Verify public CNN activations and synthetic uploads without local checkpoints."""

import argparse
import io
import json

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import torch

from .browser_ci import MODELS, native_model
from .ftp_deploy import ROOT
from .preprocess import prepare
from .qa import open_browser
from .qa_outputs import qa_outputs, qa_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://naoquerosaber.pt/AI/")
    parser.add_argument("--report", required=True)
    parser.add_argument("--screenshot-prefix", required=True)
    args = parser.parse_args()
    destination, captures = qa_outputs(args.report, args.screenshot_prefix)
    report = {"url": args.url, "checks": {}, "official_challenge": "NOT RUN"}
    image = Image.new("RGBA", (64, 64), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(26, 12), (36, 8), (36, 54)], fill="black", width=6)
    draw.line([(23, 54), (48, 54)], fill="black", width=6)
    payload = io.BytesIO()
    image.save(payload, format="PNG")
    torch.set_num_threads(2)
    with qa_report(destination, report), sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        response = page.goto(args.url)
        assert response.status == 200
        page.wait_for_function("window.digitLab?.state.ready && !digitLab.state.loading", timeout=60000)
        assert page.locator("#cnn-model").input_value() == "mnist"
        for name, folder in MODELS.items():
            mode = "letters" if name == "letters" else "digits"
            page.evaluate("async x=>await digitLab.activateMode(x.mode,x.name)",
                          {"mode": mode, "name": "mnist" if mode == "letters" else name})
            model, manifest = native_model(ROOT / "dist", name)
            fixture = json.loads((ROOT / "dist" / folder / "parity.json").read_text())
            deltas = page.evaluate("""fixture=>fixture.cases.map(c=>{
              const r=digitLab.predict(c.input),delta=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));
              return Math.max(delta(r.logits,c.logits),delta(r.hidden,c.hidden),delta(r.first,c.pool1),delta(r.second,c.pool2));
            })""", fixture)
            assert max(deltas) < 1e-4
            before = page.evaluate("digitLab.exportRecord().predictions.length")
            page.locator("#files").set_input_files({"name": "synthetic-stroke.png", "mimeType": "image/png", "buffer": payload.getvalue()})
            page.wait_for_function("n=>!digitLab.state.busy && digitLab.exportRecord().predictions.length===n", arg=before + 1)
            row = page.evaluate("digitLab.exportRecord().predictions.at(-1)")
            assert not row.get("error") and row["model_sha256"] == manifest["sha256"]
            pixels = prepare(np.asarray(image), 64 if name == "captcha-v3" else 28)
            with torch.no_grad():
                expected = model(torch.from_numpy(pixels[None])).softmax(1).numpy()[0]
            np.testing.assert_allclose(row["scores"], expected, atol=1e-5, rtol=0)
            report["checks"][name] = {"status": "PASS", "activation_error": max(deltas),
                                      "upload_score_error": float(np.max(np.abs(expected - row["scores"]))) }
        with page.expect_download():
            page.locator("#export").click()
        page.screenshot(path=str(captures["desktop"]), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
        page.screenshot(path=str(captures["mobile"]), full_page=True)
        assert not errors, errors
        report["checks"]["export_mobile_script_errors"] = "PASS"
        browser.close()
    print(json.dumps({"status": "PASS", "report": args.report}))


if __name__ == "__main__":
    main()
