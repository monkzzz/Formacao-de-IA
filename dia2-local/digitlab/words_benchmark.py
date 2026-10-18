"""Compare browser handwriting candidates on a small, explicitly identified sample."""

import argparse
import base64
import hashlib
import json
import time

from .platform_support import font_root, resolve_fonts
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


MODELS = {
    "small": ("Xenova/trocr-small-handwritten", "2432e24d184b1d964d07ed04f5d9e21d31a59141", True),
    "small-fp32": ("Xenova/trocr-small-handwritten", "2432e24d184b1d964d07ed04f5d9e21d31a59141", False),
    "base": ("Xenova/trocr-base-handwritten", "e301d1c4c4d4ece88f164518eb7aee07062eaca2", True),
}


def edit_distance(reference, predicted):
    previous = list(range(len(predicted) + 1))
    for row, left in enumerate(reference, 1):
        current = [row]
        for column, right in enumerate(predicted, 1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (left != right)))
        previous = current
    return previous[-1]


def metrics(rows):
    char_errors = sum(edit_distance(r["expected"], r["predicted"]) for r in rows)
    word_errors = sum(edit_distance(r["expected"].split(), r["predicted"].split()) for r in rows)
    characters = sum(len(r["expected"]) for r in rows)
    words = sum(len(r["expected"].split()) for r in rows)
    return {"samples": len(rows), "character_error_rate": char_errors / max(1, characters),
            "word_error_rate": word_errors / max(1, words),
            "exact_matches": sum(r["expected"] == r["predicted"] for r in rows),
            "mean_inference_ms": sum(r["elapsed_ms"] for r in rows) / max(1, len(rows))}


def fixtures(split, count, offset=0, stride=1):
    folder = ROOT / "data/words-evaluation" / split
    if offset or stride != 1:
        folder = folder / f"offset-{offset}-stride-{stride}-count-{count}"
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["human_count"] != count:
            raise ValueError("Cached fixture count differs; use a separate sampling configuration")
        return manifest
    api = "https://datasets-server.huggingface.co/rows?dataset=Teklia/IAM-line&config=default"
    rows = []
    for index in range(offset, offset + count * stride, stride):
        with urlopen(f"{api}&split={split}&offset={index}&length=1", timeout=60) as response:
            rows.extend(json.load(response)["rows"])
    samples = []
    for item in rows:
        row = item["row"]
        target = folder / f"iam-{item['row_idx']:04d}.jpg"
        with urlopen(row["image"]["src"], timeout=60) as response:
            target.write_bytes(response.read())
        samples.append({"id": f"iam-{split}-{item['row_idx']}", "kind": "human-line",
                        "path": str(target.relative_to(ROOT)), "expected": row["text"],
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    # Synthetic words exercise the short-input use case separately from real IAM lines.
    words = (["Hello", "World", "Machine", "Learning", "Morning", "Browser", "Simple", "Writing"]
             if split == "validation" else
             ["Welcome", "Today", "Computer", "Science", "School", "Private", "Neural", "Reading"])
    if split == "test" and offset:
        words = ["Tomorrow", "Example", "Human", "Window", "Letter", "Student", "People", "Friendly"]
    font = ImageFont.truetype(str(resolve_fonts(font_root(), ["segoepr.ttf"])[0]), 80)
    for i, word in enumerate(words):
        box = font.getbbox(word)
        image = Image.new("RGB", (box[2] - box[0] + 60, box[3] - box[1] + 60), "white")
        ImageDraw.Draw(image).text((30 - box[0], 30 - box[1]), word, font=font, fill="#14251d")
        target = folder / f"synthetic-{i:02d}.png"
        image.save(target)
        samples.append({"id": f"synthetic-{split}-{i}", "kind": "synthetic-word",
                        "path": str(target.relative_to(ROOT)), "expected": word,
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    manifest = {"dataset": "Teklia/IAM-line", "dataset_api": api,
                "split": split, "human_count": count, "offset": offset, "stride": stride, "synthetic_font": "Segoe Print",
                "note": "Small deterministic subset; synthetic words are not human handwriting. No training.",
                "samples": samples}
    write_json(manifest_path, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8770/")
    parser.add_argument("--split", choices=["validation", "test"], default="validation")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--candidates", nargs="+", default=["small:1:legacy", "small:3:direct", "base:1:direct", "base:3:direct"])
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    destination = ROOT / "reports" / args.report
    if destination.exists():
        raise SystemExit("Refusing to overwrite benchmark evidence")
    manifest = fixtures(args.split, args.count, args.offset, args.stride)
    report = {"status": "RUNNING", "split": args.split, "fixtures": manifest,
              "note": "Small sample comparison, not a full IAM benchmark or independent training-set audit.",
              "candidates": {}}
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        for candidate in args.candidates:
            name, beam_count, preparation = candidate.split(":")
            model, revision, quantized = MODELS[name]
            print(f"Loading {candidate}", flush=True)
            started = time.monotonic()
            page.evaluate("""async ({model,revision,quantized}) => {
              if (window.benchmarkModel === model+quantized) return;
              if (window.benchmarkPipe) {await window.benchmarkPipe.dispose();window.benchmarkPipe=null;}
              const {pipeline,env}=await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js');
              env.allowLocalModels=false;env.backends.onnx.wasm.numThreads=1;
              window.benchmarkPipe=await pipeline('image-to-text',model,{revision,quantized});
              window.benchmarkModel=model+quantized;
            }""", {"model": model, "revision": revision, "quantized": quantized})
            result = {"model": model, "revision": revision, "beams": int(beam_count),
                      "preparation": preparation, "quantized": quantized, "load_seconds": time.monotonic() - started, "rows": []}
            report["candidates"][candidate] = result
            for sample in manifest["samples"]:
                image_bytes = (ROOT / sample["path"]).read_bytes()
                image = "data:image/png;base64," + base64.b64encode(image_bytes).decode()
                prediction = page.evaluate("""async ({image,beams,preparation}) => {
                  const {prepareWord}=await import('./v3/words.js?v=3.1.0');
                  const bitmap=await createImageBitmap(await (await fetch(image)).blob());
                  const source=document.createElement('canvas');source.width=bitmap.width;source.height=bitmap.height;
                  source.getContext('2d').drawImage(bitmap,0,0);bitmap.close();
                  let prepared=prepareWord(source);
                  if (preparation==='legacy') {
                    const display=document.createElement('canvas');display.width=1000;display.height=300;
                    const ctx=display.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,1000,300);
                    const scale=Math.min(968/prepared.width,268/prepared.height);
                    ctx.drawImage(prepared,(1000-prepared.width*scale)/2,(300-prepared.height*scale)/2,prepared.width*scale,prepared.height*scale);
                    prepared=prepareWord(display);
                  }
                  const start=performance.now();
                  const output=await window.benchmarkPipe(prepared.toDataURL('image/png'),{max_new_tokens:64,num_beams:beams});
                  return {predicted:output[0].generated_text.trim(),elapsed_ms:performance.now()-start};
                }""", {"image": image, "beams": int(beam_count), "preparation": preparation})
                result["rows"].append({"id": sample["id"], "kind": sample["kind"],
                                       "expected": sample["expected"], **prediction})
                write_json(destination, report)
                print(f"{candidate}: {len(result['rows'])}/{len(manifest['samples'])}", flush=True)
            result["metrics"] = {kind: metrics([row for row in result["rows"] if row["kind"] == kind])
                                 for kind in ("human-line", "synthetic-word")}
            print(json.dumps({candidate: result["metrics"]}), flush=True)
            write_json(destination, report)
        browser.close()
    report["status"] = "PASS"
    write_json(destination, report)


if __name__ == "__main__":
    main()
