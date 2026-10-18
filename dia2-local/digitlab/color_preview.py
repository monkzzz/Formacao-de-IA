"""Actual uploads and feature parity for isolated color-aware preprocessing."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import shutil
import threading

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .captcha_extension import baseline_model
from .color_preprocess import VERSION, prepare_color
from .color_study import DIRECTORY, NAME, REPORT, verify
from .preprocessing_study import digest
from .qa import open_browser
from .train import ROOT, write_json

PREVIEW = ROOT / ".tmp" / (NAME + "-preview")
OUTPUT = ROOT / "reports" / (NAME + "-browser.json")


def main():
    if PREVIEW.exists() or OUTPUT.exists():
        raise FileExistsError("Preserve completed preview")
    metadata = json.loads(REPORT.read_text())
    if metadata["status"] != "DEVELOPMENT COMPLETE":
        raise ValueError("Finish frozen development comparison first")
    verify(metadata)
    (PREVIEW / "v3").mkdir(parents=True)
    for name in ("inference.js", "residual.js"):
        shutil.copy2(ROOT / "dist/v3" / name, PREVIEW / "v3" / name)
    shutil.copy2(ROOT / "digitlab/color_preprocess.js", PREVIEW / "v3/preprocess.js")
    folder = PREVIEW / "model/captcha-v3/digits"
    folder.mkdir(parents=True)
    original = ROOT / "dist/model/captcha-v3/digits"
    shutil.copy2(original / "weights.bin", folder / "weights.bin")
    manifest = json.loads((original / "manifest.json").read_text())
    manifest.update(preprocessing=VERSION, preview_scope="Isolated RGB development parity; active app unchanged")
    write_json(folder / "manifest.json", manifest)
    (PREVIEW / "index.html").write_text('''<!doctype html><meta charset="utf-8">
<title>Color-aware development preview</title><h1>Color-aware development preview</h1>
<p>Frozen residual weights. Experimental RGB foreground; active app unchanged.</p>
<input id="files" type="file" multiple accept="image/png"><pre id="result">Loading…</pre>
<script type="module">
import {loadModel,predict} from './v3/inference.js?v=color-preview';
import {prepareCanvas,prepareRGBA} from './v3/preprocess.js?v=3.6.0';
const model=await loadModel('digits','captcha-v3');
window.preview={model,records:[],ready:true,busy:false,predict:input=>predict(model,Float32Array.from(input)),prepareRGBA};
document.querySelector('#result').textContent='Verified model ready; select independent development fixtures.';
document.querySelector('#files').addEventListener('change',async e=>{
 preview.busy=true;
 try {for(const file of e.target.files) {
  const bitmap=await createImageBitmap(file),canvas=document.createElement('canvas');
  canvas.width=bitmap.width;canvas.height=bitmap.height;canvas.getContext('2d').drawImage(bitmap,0,0);bitmap.close();
  try {const input=prepareCanvas(canvas,64),r=predict(model,input);
   preview.records.push({file:file.name,input:Array.from(input),scores:r.scores,predicted:r.digit,rejected:false});
  } catch(error) {preview.records.push({file:file.name,rejected:true,error:String(error)});}
 }} finally {preview.busy=false;document.querySelector('#result').textContent=JSON.stringify(preview.records.map(r=>({file:r.file,predicted:r.predicted,rejected:r.rejected})),null,2);}
});
</script>''')
    frozen = {str(p.relative_to(PREVIEW)): digest(p) for p in PREVIEW.rglob("*") if p.is_file()}
    freeze = {"preview_sha256": frozen, "model_sha256": manifest["sha256"], "study_sha256": digest(REPORT),
              "collector_sha256": digest(ROOT / "digitlab/color_preview.py")}
    write_json(ROOT / "reports" / (NAME + "-preview-freeze.json"), freeze)
    indices = [*range(0, 1200, 60), *range(1200, 1800, 15)]
    paths = [DIRECTORY / "fixtures" / f"sample-{i:04d}.png" for i in indices]
    torch.set_num_threads(2)
    model = baseline_model().eval()
    expected = [prepare_color(np.asarray(Image.open(p).convert("RGBA"))) for p in paths]
    with torch.no_grad():
        tensors = torch.from_numpy(np.stack(expected))
        logits = model(tensors)
        scores = logits.softmax(1).numpy()
        first, second, hidden = model.features(tensors[:3])
    report = {"status": "FAIL", "model_sha256": manifest["sha256"], "preprocessing": VERSION,
              "study_sha256": digest(REPORT), "scope": "Isolated browser uploads; active interface untouched",
              "reserved_or_official_inputs_used": False, "upload_indices": indices}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(PREVIEW)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))
            url = f"http://127.0.0.1:{server.server_port}/"
            page.goto(url)
            page.wait_for_function("window.preview?.ready===true")
            assert page.evaluate("preview.model.manifest.sha256") == manifest["sha256"]
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("preview.records.length===60&&!preview.busy", timeout=120000)
            records = page.evaluate("preview.records")
            prep_error = score_error = 0.
            for i, row in enumerate(records):
                if row["rejected"] or row["file"] != paths[i].name:
                    raise ValueError("Upload rejected or reordered")
                prep_error = max(prep_error, float(np.max(np.abs(expected[i].flatten() - row["input"]))))
                score_error = max(score_error, float(np.max(np.abs(scores[i] - row["scores"]))))
                assert row["predicted"] == int(scores[i].argmax())
            assert prep_error <= 1e-6 and score_error <= 1e-5
            cases = [{"input": expected[i].flatten().tolist(), "logits": logits[i].tolist(),
                      "first": first[i].flatten().tolist(), "second": second[i].flatten().tolist(),
                      "hidden": hidden[i].tolist()} for i in range(3)]
            parity = page.evaluate('''cases=>cases.map(c=>{const r=preview.predict(c.input);return Object.fromEntries(['logits','first','second','hidden'].map(k=>[k,Math.max(...Array.from(r[k],(v,i)=>Math.abs(v-c[k][i])))]));})''', cases)
            assert all(v < 1e-4 for c in parity for v in c.values())
            # Direct browser preparation adds alpha, both input sizes and blank rejection.
            edge_count = 0
            for side in (28, 64):
                rgba = np.asarray(Image.open(paths[-1]).convert("RGBA")).copy()
                rgba[:3, :, 3] = 0
                result = page.evaluate("o=>Array.from(preview.prepareRGBA(o.data,o.width,o.height,o.side))",
                                       {"data": rgba.flatten().tolist(), "width": rgba.shape[1], "height": rgba.shape[0], "side": side})
                np.testing.assert_allclose(result, prepare_color(rgba, side).flatten(), atol=1e-6, rtol=0)
                edge_count += 1
            rejected = page.evaluate("()=>{try{preview.prepareRGBA(new Uint8Array(8*8*4).fill(255),8,8,64);return false;}catch{return true;}}")
            assert rejected
            times = page.evaluate("input=>{preview.predict(input);return Array.from({length:30},()=>{const t=performance.now();preview.predict(input);return performance.now()-t;});}", cases[0]["input"])
            p95 = float(np.percentile(times, 95))
            assert p95 < 150
            if errors or any(r["method"] != "GET" or not r["url"].startswith((url, "blob:")) for r in requests):
                raise ValueError("Page error or non-static request")
            verify(metadata)
            assert all(digest(PREVIEW / p) == value for p, value in frozen.items())
            report.update(status="PASS", upload_count=60, maximum_input_error=prep_error,
                          maximum_score_error=score_error, activation_errors=parity,
                          alpha_and_input_size_cases=edge_count, blank_rejection="PASS", p95_ms=p95,
                          browser_version=browser.version, page_errors=errors, requests=requests,
                          preserved_app_and_models="PASS", frozen_preview_unchanged=True)
            screenshot = ROOT / "reports/screenshots" / (NAME + "-preview.png")
            screenshot.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(screenshot))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        write_json(OUTPUT, report)
    print("PASS: 60 actual RGB uploads, input/score/activation parity, alpha/rejection and speed")


if __name__ == "__main__":
    main()
