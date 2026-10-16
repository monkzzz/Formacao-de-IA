"""Browser activation parity and latency gate before opening residual test data."""

import argparse
import json

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .highres import export
from .preprocess import prepare
from .qa import open_browser
from .residual import ARCHITECTURE, POLICY, ResidualCNN
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8770/")
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--report", default="captcha-v3-speed-qa.json")
    parser.add_argument("--interface", action="store_true", help="Check the selected model in the full UI after the test gate")
    args = parser.parse_args()
    target = ROOT / "reports" / args.report
    assert not target.exists(), "Preserve previous reports"
    torch.set_num_threads(2)
    directory = ROOT / "dist/model/captcha-v3/digits"
    if args.development:
        directory = ROOT / "artifacts/residual-runtime-development/digits"
        if not directory.exists():
            torch.manual_seed(73)
            model = ResidualCNN()
            model.load_state_dict(torch.load(ROOT / "artifacts/captcha-v2/best.pt", map_location="cpu", weights_only=True), strict=False)
            # Nonzero blocks exercise signed skip additions, not just identity paths.
            torch.nn.init.normal_(model.block1.expand.weight, std=.02)
            torch.nn.init.normal_(model.block2.expand.weight, std=.02)
            inputs = torch.from_numpy(np.stack([prepare(np.asarray(Image.open(
                ROOT / f"reports/mnist-fixtures/digit-{i}.png").convert("RGBA")), 64) for i in range(10)]))
            manifest = export(model, directory, {"status": "Untrained runtime fixture; no accuracy claim"}, inputs)
            manifest["architecture"] = ARCHITECTURE
            write_json(directory / "manifest.json", manifest)
    manifest = json.loads((directory / "manifest.json").read_text())
    fixture = json.loads((directory / "parity.json").read_text())
    baseline_fixture = json.loads((ROOT / "dist/model/captcha-v2/digits/parity.json").read_text())
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        if args.development:
            for name, kind in (("manifest.json", "application/json"), ("weights.bin", "application/octet-stream")):
                page.route(f"**/model/captcha-v3/digits/{name}*",
                           lambda route, request, name=name, kind=kind: route.fulfill(path=str(directory / name), content_type=kind))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        result = page.evaluate("""async ({candidateFixture,baselineFixture}) => {
          const {loadModel,predict} = await import('./v3/inference.js?v=residual-test');
          const candidate=await loadModel('digits','captcha-v3'),baseline=await loadModel('digits','captcha-v2');
          const parity=candidateFixture.cases.map(item=>{
            const p=predict(candidate,Float32Array.from(item.input));
            const error=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));
            return {label:item.label,logits:error(p.logits,item.logits),first:error(p.first,item.pool1),
              second:error(p.second,item.pool2),hidden:error(p.hidden,item.hidden)};
          });
          const measure=(model,fixture)=>{
            const inputs=fixture.cases.map(c=>Float32Array.from(c.input)),times=[];
            for(let pass=0;pass<5;pass++) for(const input of inputs){
              const start=performance.now();predict(model,input);
              if(pass)times.push(performance.now()-start);
            }
            times.sort((a,b)=>a-b);
            return {count:times.length,median_ms:times[Math.floor(times.length/2)],p95_ms:times[Math.floor(times.length*.95)]};
          };
          let rejected=false;
          try{predict(candidate,Float32Array.of(NaN));}catch{rejected=true;}
          return {sha256:candidate.manifest.sha256,parity,latency:{baseline:measure(baseline,baselineFixture),
            candidate:measure(candidate,candidateFixture)},invalid_input_rejected:rejected};
        }""", {"candidateFixture": fixture, "baselineFixture": baseline_fixture})
        assert result["sha256"] == manifest["sha256"]
        assert all(row[k] <= .0001 for row in result["parity"] for k in ("logits", "first", "second", "hidden")), result["parity"]
        assert result["invalid_input_rejected"] and not errors
        assert result["latency"]["candidate"]["p95_ms"] < POLICY["desktop_p95_limit_ms"], result["latency"]
        interface = {}
        if args.interface:
            assert not args.development
            assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
            assert "Residual" in page.locator("#architecture").inner_text()
            for mode, side, first, second in (("digits", 64, 32, 8), ("letters", 28, 14, 7)):
                page.evaluate("mode=>digitLab.activateMode(mode)", mode)
                assert page.locator("#prepared").get_attribute("width") == str(side)
                assert page.locator("#layer-one canvas").first.get_attribute("width") == str(first)
                assert page.locator("#layer-two canvas").first.get_attribute("width") == str(second)
            page.evaluate("digitLab.activateMode('words')")
            assert page.locator("#words-workspace").is_visible()
            page.evaluate("digitLab.activateMode('digits')")
            cached = page.evaluate("""async()=>{
              const previous=await import('./v3/inference.js?v=captcha-2');
              const old=await import('./v3/inference.js?v=captcha-1');
              return [(await previous.loadModel()).manifest.sha256,(await old.loadModel()).inputSide];
            }""")
            assert cached == [baseline_fixture["model_sha256"], 28]
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=str(ROOT / "reports/screenshots" / (target.stem + "-mobile.png")), full_page=True)
            interface = {"mode_dimensions": True, "words_entry": True, "cached_previous_models": True,
                         "mobile_layout": True, "active_residual_model": True}
        assert not errors, errors
        browser.close()
    write_json(target, {"status": "PASS", "model_sha256": manifest["sha256"], "url": args.url,
        "scope": "Untrained development runtime" if args.development else "Frozen development choice, before fresh test",
        "latency_scope": "Headless desktop Edge on training machine; not physical-phone performance",
        "latency": result["latency"], "activation_parity": result["parity"],
        "invalid_input_rejected": True, "page_errors": errors, "interface": interface})
    print(json.dumps({"status": "PASS", "latency": result["latency"]}))


if __name__ == "__main__":
    main()
