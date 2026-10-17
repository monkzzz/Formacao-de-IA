"""Verify the selected fixed-weight preparation in an isolated browser harness."""

import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from functools import partial
import shutil
import threading

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .preprocessing_study import DIRECTORY, NAME, REPORT, digest
from .preprocessing_variants import prepare_variant
from .qa import open_browser
from .residual import ResidualCNN
from .train import ROOT, write_json

PREVIEW = ROOT / ".tmp" / (NAME + "-preview")
OUTPUT = ROOT / "reports" / (NAME + "-browser.json")
VERSION = "border-gray-bilinear-com-64-small-components-v1"
FILTER = """
  if (side === 64) {
    const seen = new Uint8Array(ink.length), components = [];
    for (let at = 0; at < ink.length; at++) {
      if (seen[at] || ink[at] <= 0) continue;
      const stack = [at], component = []; seen[at] = 1;
      while (stack.length) {
        const index = stack.pop(), y = Math.floor(index / width), x = index % width;
        component.push(index);
        for (let dy=-1;dy<=1;dy++) for(let dx=-1;dx<=1;dx++) {
          const ny=y+dy,nx=x+dx,next=ny*width+nx;
          if(ny>=0&&ny<height&&nx>=0&&nx<width&&!seen[next]&&ink[next]>0) {
            seen[next]=1;stack.push(next);
          }
        }
      }
      components.push(component);
    }
    const largest=components.reduce((n,c)=>Math.max(n,c.length),0);
    const maximum=Math.max(4,Math.ceil(.0008*ink.length));
    for(const c of components) if(c.length<.015*largest&&c.length<maximum) for(const i of c) ink[i]=0;
    left=width;right=-1;top=height;bottom=-1;
    for(let y=0;y<height;y++) for(let x=0;x<width;x++) if(ink[y*width+x]>.20) {
      left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);
    }
  }
"""


def main():
    if PREVIEW.exists() or OUTPUT.exists():
        raise FileExistsError("Preserve completed isolated preview")
    metadata = json.loads(REPORT.read_text())
    if metadata.get("selected_variant") != "small_components" or not metadata["variants"]["small_components"]["eligible"]:
        raise ValueError("This isolated port requires the selected small-components variant")
    for name, value in metadata["source_sha256"].items():
        if digest(ROOT / "digitlab" / name) != value:
            raise ValueError("Study source changed")
    for name, value in metadata["preserved_sha256"].items():
        if digest(ROOT / name) != value:
            raise ValueError("Preserved model/app changed")
    (PREVIEW / "v3").mkdir(parents=True)
    for name in ("preprocess.js", "inference.js", "residual.js"):
        shutil.copy2(ROOT / "dist/v3" / name, PREVIEW / "v3" / name)
    source = (PREVIEW / "v3/preprocess.js").read_text()
    marker = "  if (right < left) throw new Error(\"No visible digit.\");"
    if source.count(marker) != 1:
        raise ValueError("Unexpected original preprocessing implementation")
    source = source.replace('"border-gray-bilinear-com-64-v1"', json.dumps(VERSION)).replace(marker, FILTER + marker)
    (PREVIEW / "v3/preprocess.js").write_text(source)
    folder = PREVIEW / "model/captcha-v3/digits"
    folder.mkdir(parents=True)
    original = ROOT / "dist/model/captcha-v3/digits"
    shutil.copy2(original / "weights.bin", folder / "weights.bin")
    manifest = json.loads((original / "manifest.json").read_text())
    manifest.update(preprocessing=VERSION, preview_scope="Fixed weights, selected development preprocessing; reserved/official results NOT RUN")
    write_json(folder / "manifest.json", manifest)
    (PREVIEW / "index.html").write_text("""<!doctype html><meta charset="utf-8"><title>Fixed-weight preprocessing parity</title>
<h1>Isolated development preview</h1><p>Browser/Python parity harness. No active application or model replacement.</p>
<input id="files" type="file" multiple accept="image/png"><pre id="result">Loading…</pre>
<script type="module">
import {loadModel,predict} from './v3/inference.js?v=preprocessing-preview';
import {prepareCanvas} from './v3/preprocess.js?v=3.6.0';
const model=await loadModel('digits','captcha-v3');
window.preview={model,records:[],ready:true,predict:input=>predict(model,Float32Array.from(input)),prepareCanvas,busy:false};
document.getElementById('result').textContent='Fixed weights verified; development preview ready.';
document.getElementById('files').addEventListener('change',async event=>{
 preview.busy=true;
 try {for(const file of event.target.files) {
  const bitmap=await createImageBitmap(file),canvas=document.createElement('canvas');
  canvas.width=bitmap.width;canvas.height=bitmap.height;canvas.getContext('2d').drawImage(bitmap,0,0);bitmap.close();
  const input=prepareCanvas(canvas,64),result=predict(model,input);
  preview.records.push({file:file.name,input:Array.from(input),scores:result.scores,predicted:result.digit});
 }} finally {preview.busy=false;document.getElementById('result').textContent=JSON.stringify(preview.records.map(r=>({file:r.file,predicted:r.predicted})),null,2);}
});
</script>""")
    files = {str(p.relative_to(PREVIEW)): digest(p) for p in PREVIEW.rglob("*") if p.is_file()}
    freeze = {"scope": "Isolated development parity; fixed weights; no reserved/official challenge inference",
              "files": files, "model_sha256": manifest["sha256"], "preprocessing": VERSION,
              "helper_sha256": digest(ROOT / "digitlab/preprocessing_preview.py"), "study_report_sha256": digest(REPORT)}
    freeze_path = ROOT / "reports" / (NAME + "-preview-freeze.json")
    with freeze_path.open("x") as stream:
        json.dump(freeze, stream, indent=2)
    torch.set_num_threads(2)
    model = ResidualCNN()
    model.load_state_dict(torch.load(ROOT / "artifacts/captcha-v3/best.pt", map_location="cpu", weights_only=True))
    model.eval()
    paths = sorted((DIRECTORY / "fixtures").glob("sample-*.png"))[:60]
    expected = np.stack([prepare_variant(np.asarray(Image.open(p).convert("RGBA")), "small_components") for p in paths])
    with torch.no_grad():
        logits = model(torch.from_numpy(expected))
        scores = logits.softmax(1).numpy()
        first, second, hidden = model.features(torch.from_numpy(expected[:3]))
    report = {"status": "FAIL", "freeze_sha256": digest(freeze_path), "model_sha256": manifest["sha256"],
              "preprocessing": VERSION, "reserved_or_official_evaluation": "NOT RUN", "publication": "NOT RUN"}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(PREVIEW)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))
            url = f"http://127.0.0.1:{server.server_port}/"
            page.goto(url)
            page.wait_for_function("window.preview?.ready === true")
            if page.evaluate("preview.model.manifest.sha256") != manifest["sha256"]:
                raise ValueError("Wrong browser weights")
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("preview.records.length === 60 && !preview.busy", timeout=120000)
            records = page.evaluate("preview.records")
            prep_error = score_error = 0.
            for i, record in enumerate(records):
                if record["file"] != paths[i].name:
                    raise ValueError("Upload ordering mismatch")
                prep_error = max(prep_error, float(np.max(np.abs(expected[i].flatten() - record["input"]))))
                score_error = max(score_error, float(np.max(np.abs(scores[i] - record["scores"]))))
                if record["predicted"] != int(scores[i].argmax()):
                    raise ValueError("Browser/Python class mismatch")
            if prep_error > 1e-6 or score_error > 1e-5:
                raise ValueError("Browser/Python upload mismatch")
            fixtures = [{"input": expected[i].flatten().tolist(), "logits": logits[i].tolist(),
                         "pool1": first[i].flatten().tolist(), "pool2": second[i].flatten().tolist(), "hidden": hidden[i].tolist()} for i in range(3)]
            parity = page.evaluate("""cases => cases.map(item=>{
              const result=preview.predict(item.input),delta=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));
              return {logits:delta(result.logits,item.logits),pool1:delta(result.first,item.pool1),pool2:delta(result.second,item.pool2),hidden:delta(result.hidden,item.hidden)};
            })""", fixtures)
            if any(value > 1e-4 for row in parity for value in row.values()):
                raise ValueError("Activation mismatch")
            timing = page.evaluate("""input=>{preview.predict(input);return Array.from({length:30},()=>{const t=performance.now();preview.predict(input);return performance.now()-t;});}""", fixtures[0]["input"])
            if errors or any(r["method"] != "GET" or not r["url"].startswith((url, "blob:")) for r in requests):
                raise ValueError("Page error or unexpected non-static request")
            if any(digest(PREVIEW / name) != h for name,h in files.items()):
                raise ValueError("Preview changed during QA")
            report.update(status="PASS", uploads=60, preprocessing_max_error=prep_error, scores_max_error=score_error,
                          activations=parity, median_inference_ms=float(np.median(timing)), p95_inference_ms=float(np.percentile(timing,95)),
                          static_get_requests=len(requests), page_errors=errors)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        with OUTPUT.open("x") as stream:
            json.dump(report, stream, indent=2)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
