"""Freeze development decisions and verify diagnostic ensemble parity/speed."""

import hashlib
import json
from datetime import datetime, timezone

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from .ensemble_benchmark import NAME, POLICY, load_models, mix_scores, scores
from .preprocess import prepare
from .qa import open_browser
from .train import ROOT, write_json


def main():
    report_path = ROOT / "reports/ensemble-v1-speed-qa.json"
    freeze_path = ROOT / "reports/ensemble-v1-evaluation-freeze.json"
    if report_path.exists() or freeze_path.exists():
        raise SystemExit("Preserve existing verification and freeze records")
    directory = ROOT / "artifacts" / NAME
    selection = json.loads((directory / "selection.json").read_text())
    development = json.loads((ROOT / "reports/ensemble-v1-development.json").read_text())
    candidates = [c for c in development["candidates"] if c["eligible"] and c["high_resolution_weight"] not in (0, 1)]
    candidate = min(candidates, key=lambda c: (-c["overall"]["correct"], c["overall"]["loss"], -c["high_resolution_weight"]))
    weight = candidate["high_resolution_weight"]
    models = load_models()
    assert models[2] == selection["model_identities"]
    fixtures = json.loads((directory / "development/fixtures/labels.json").read_text())
    paths = [directory / "development/fixtures" / row["file"] for row in fixtures]
    images = [np.asarray(Image.open(path).convert("RGBA")) for path in paths]
    low_inputs = np.stack([prepare(image) for image in images])
    high_inputs = np.stack([prepare(image, 64) for image in images])
    expected = mix_scores(scores(models[0], low_inputs), scores(models[1], high_inputs), weight)
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8769/")
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        result = page.evaluate("""async ({cases,weight}) => {
          const {loadModel,predict}=await import('./v3/inference.js?v=captcha-2');
          const {prepareRGBA}=await import('./v3/preprocess.js?v=3.6.0');
          const low=await loadModel('digits','captcha-v1'),high=digitLab.state.model;
          const prepared=cases.map(item=>({low:prepareRGBA(item.data,item.width,item.height,28),
            high:prepareRGBA(item.data,item.width,item.height,64)}));
          const combined=prepared.map(item=>{
            const a=predict(low,item.low),b=predict(high,item.high);
            return a.scores.map((value,i)=>value*(1-weight)+b.scores[i]*weight);
          });
          const measure=(ensemble)=>{
            const times=[];
            for(let pass=0;pass<3;pass++) for(const item of prepared.slice(0,20)) {
              const start=performance.now(),b=predict(high,item.high);
              if(ensemble) {
                const a=predict(low,item.low);
                a.scores.map((value,i)=>value*(1-weight)+b.scores[i]*weight);
              }
              if(pass) times.push(performance.now()-start);
            }
            times.sort((a,b)=>a-b);
            return {count:times.length,median_ms:times[Math.floor(times.length/2)],p95_ms:times[Math.floor(times.length*.95)]};
          };
          return {combined,baseline:measure(false),ensemble:measure(true),
            identities:{'captcha-v1':low.manifest.sha256,'captcha-v2':high.manifest.sha256}};
        }""", {"weight": weight, "cases": [{"data": image.flatten().tolist(), "width": image.shape[1], "height": image.shape[0]} for image in images]})
        assert result["identities"] == selection["model_identities"]
        np.testing.assert_allclose(result["combined"], expected, atol=1e-5, rtol=0)
        assert np.asarray(result["combined"]).argmax(1).tolist() == expected.argmax(1).tolist()
        assert result["ensemble"]["p95_ms"] < POLICY["desktop_p95_limit_ms"]
        browser.close()
    freeze = {"frozen_at": datetime.now(timezone.utc).isoformat(), "model_identities": models[2],
        "deployment_high_resolution_weight": selection["high_resolution_weight"],
        "diagnostic_ensemble_weight": weight, "ensemble_selected": selection["ensemble_selected"],
        "development_report_sha256": hashlib.sha256((ROOT / "reports/ensemble-v1-development.json").read_bytes()).hexdigest(),
        "selection_sha256": hashlib.sha256((directory / "selection.json").read_bytes()).hexdigest(),
        "scope": "Deployment choice and best development ensemble frozen before test data; diagnostic test cannot change deployment selection",
        "test_inputs_loaded": False}
    write_json(freeze_path, freeze)
    write_json(report_path, {"status": "PASS", "model_identities": models[2],
        "high_resolution_weight": weight, "selected_deployment_weight": selection["high_resolution_weight"],
        "p95_ms": result["ensemble"]["p95_ms"], "baseline_latency": result["baseline"],
        "ensemble_latency": result["ensemble"], "parity_count": len(paths),
        "maximum_score_error": float(np.max(np.abs(np.asarray(result["combined"]) - expected))),
        "scope": "Headless desktop Edge, inference only; preprocessing parity checked separately; physical phone NOT RUN"})
    print(json.dumps({"status": "PASS", "weight": weight, "baseline": result["baseline"], "ensemble": result["ensemble"]}))


if __name__ == "__main__":
    main()
