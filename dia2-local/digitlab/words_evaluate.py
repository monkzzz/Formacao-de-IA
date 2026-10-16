"""Frozen, resumable larger browser evaluation; no training or model selection."""

import argparse
import base64
import hashlib
import io
import json
import random
import re
import time
from datetime import datetime, timezone
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json
from .words_benchmark import edit_distance


DATASET = "Teklia/IAM-line"
REVISION = "fbdad97500ce54635c0d1ba306bf535cb40656cf"
TOTAL = 2915
SOURCE_FILES = ["dist/v3/words.js", "dist/v3/words-worker.js", "dist/v3/canvas-tools.js"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_url(url):
    for attempt in range(6):
        try:
            with urlopen(url, timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 5:
                raise
            time.sleep(min(16, 2 ** attempt))


def prepare(name, count, seed):
    protocol_path = ROOT / "reports" / f"{name}-protocol.json"
    if protocol_path.exists():
        raise SystemExit("Protocol already frozen; use --run or a new evaluation name")
    excluded = set()
    for report_name in ("words-precision-test.json", "words-fp32-fresh-test.json"):
        previous = json.loads((ROOT / "reports" / report_name).read_text(encoding="utf-8"))
        for sample in previous["fixtures"]["samples"]:
            if sample["kind"] == "human-line":
                excluded.add(int(sample["id"].rsplit("-", 1)[1]))
    selected = sorted(random.Random(seed).sample([i for i in range(TOTAL) if i not in excluded], count))
    folder = ROOT / "data/words-evaluation" / name
    folder.mkdir(parents=True, exist_ok=True)
    import pyarrow.parquet as parquet
    metadata = json.loads(read_url(f"https://huggingface.co/api/datasets/{DATASET}/tree/{REVISION}/data"))
    source = next(item for item in metadata if item["path"] == "data/test.parquet")
    source_url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{source['path']}"
    source_path = folder / "test.parquet"
    expected_hash = source.get("lfs", {}).get("oid")
    if not source_path.exists():
        temporary = source_path.with_suffix(".parquet.part")
        with urlopen(source_url, timeout=60) as response, temporary.open("wb") as handle:
            downloaded, next_notice = 0, 16 * 1024 * 1024
            while block := response.read(1024 * 1024):
                handle.write(block); downloaded += len(block)
                if downloaded >= next_notice:
                    print(f"Downloaded test file: {downloaded // (1024 * 1024)} MiB", flush=True)
                    next_notice += 16 * 1024 * 1024
        temporary.replace(source_path)
    source_hash = digest(source_path.read_bytes())
    assert source_path.stat().st_size == source["size"]
    if expected_hash:
        assert source_hash == expected_hash
    table = parquet.read_table(source_path)
    assert table.num_rows == TOTAL
    rows = table.take(selected).to_pylist()
    samples = []
    for index, row in zip(selected, rows):
        data = row["image"]["bytes"]
        path = folder / f"line-{index:04d}.jpg"
        path.write_bytes(data)
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
        samples.append({"row": index, "path": str(path.relative_to(ROOT)), "text": row["text"],
                        "sha256": digest(data), "width": width, "height": height})
        if len(samples) % 100 == 0:
            print(f"Prepared {len(samples)}/{count} real handwriting lines", flush=True)
    samples.sort(key=lambda sample: sample["row"])
    manifest_path = folder / "manifest.json"
    write_json(manifest_path, {"dataset": DATASET, "revision": REVISION, "split": "test", "samples": samples})
    version = re.search(r'id="app-version"[^>]*>v([^<]+)',
                        (ROOT / "dist/index.html").read_text(encoding="utf-8")).group(1)
    protocol = {
        "status": "FROZEN_BEFORE_INFERENCE", "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(), "application_version": version,
        "dataset": DATASET, "dataset_revision": REVISION, "split": "test", "available_rows": TOTAL,
        "source_parquet": {"url": source_url, "sha256": source_hash, "bytes": source["size"]},
        "count": count, "seed": seed, "selected_rows": selected, "excluded_previous_rows": sorted(excluded),
        "manifest": str(manifest_path.relative_to(ROOT)), "manifest_sha256": digest(manifest_path.read_bytes()),
        "source_sha256": {name: digest((ROOT / name).read_bytes()) for name in SOURCE_FILES},
        "model": "Xenova/trocr-small-handwritten", "model_revision": "2432e24d184b1d964d07ed04f5d9e21d31a59141",
        "profile": "precise", "precision": "float32", "decoding": "greedy", "workers": 2,
        "preparation": "word-crop-display-v1; original crop, white 1000x300 display canvas, final crop",
        "primary_metric": "word_accuracy = 1 - total_word_edit_distance / total_reference_word_tokens",
        "other_metrics": ["character_error_rate", "word_error_rate", "exact_line_accuracy"],
        "normalization": "Collapse whitespace and trim on both texts; preserve case and punctuation. Whitespace tokens include punctuation.",
        "failures": "Empty model output counts as deletions; infrastructure errors stop the run, without dropping samples.",
        "training_performed": False, "model_selection_performed": False,
        "note": "Evaluation of the released fixed reader; English line OCR, not isolated-word classification or a pretrained-data audit.",
    }
    write_json(protocol_path, protocol)
    print(f"FROZEN: {count} real lines, {len(excluded)} previously used rows excluded", flush=True)


HARNESS = """() => {
  window.ocrWorkers = [0,1].map(() => new Worker(new URL('./v3/words-worker.js?v=3.2.0',location.href),{type:'module'}));
  window.ocrPredict = async (lane,job) => {
    const {prepareWord}=await import('./v3/words.js?v=3.2.0');
    const bitmap=await createImageBitmap(await (await fetch(job.image)).blob());
    const source=document.createElement('canvas');source.width=bitmap.width;source.height=bitmap.height;
    source.getContext('2d').drawImage(bitmap,0,0);bitmap.close();
    const crop=prepareWord(source), display=document.createElement('canvas');
    display.width=1000;display.height=300;
    const ctx=display.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,1000,300);
    const scale=Math.min(968/crop.width,268/crop.height);
    ctx.drawImage(crop,(1000-crop.width*scale)/2,(300-crop.height*scale)/2,crop.width*scale,crop.height*scale);
    const image=prepareWord(display).toDataURL('image/png');
    return new Promise((resolve,reject)=>{
      const worker=ocrWorkers[lane];
      const timer=setTimeout(()=>reject(new Error('Worker timed out')),300000);
      worker.onerror=event=>{clearTimeout(timer);reject(new Error(event.message));};
      worker.onmessage=({data})=>{
        if(data.type==='progress')return;
        clearTimeout(timer);
        if(data.type==='error')reject(new Error(data.message));else resolve({row:job.row,...data});
      };
      worker.postMessage({id:job.row,image,profile:'precise'});
    });
  };
  window.ocrBatch = async jobs => {
    const queue=[...jobs], results=[];
    await Promise.all([0,1].map(async lane=>{
      while(queue.length){const job=queue.shift();results.push(await ocrPredict(lane,job));}
    }));
    return results;
  };
} """


def run(name, url, resume):
    protocol_path = ROOT / "reports" / f"{name}-protocol.json"
    raw_path = ROOT / "reports" / f"{name}-raw.jsonl"
    final_path = ROOT / "reports" / f"{name}-evaluation.json"
    if final_path.exists() or raw_path.exists() and not resume:
        raise SystemExit("Existing evidence found; --resume requires the same frozen protocol")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    manifest_path = ROOT / protocol["manifest"]
    assert digest(manifest_path.read_bytes()) == protocol["manifest_sha256"]
    for path, expected in protocol["source_sha256"].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
    samples = json.loads(manifest_path.read_text(encoding="utf-8"))["samples"]
    lookup = {sample["row"]: sample for sample in samples}
    records = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()] if raw_path.exists() else []
    done = {record["row"] for record in records}
    assert len(done) == len(records) and done <= set(lookup)
    remaining = [sample for sample in samples if sample["row"] not in done]
    started = time.monotonic()

    def payload(sample):
        image = (ROOT / sample["path"]).read_bytes()
        assert digest(image) == sample["sha256"]
        return {"row": sample["row"], "image": "data:image/jpeg;base64," + base64.b64encode(image).decode()}

    def record(outputs):
        for output in outputs:
            sample = lookup[output["row"]]
            assert output["model"] == protocol["model"] and output["revision"] == protocol["model_revision"]
            assert output["profile"] == "precise" and output["precision"] == "float32"
            expected = " ".join(sample["text"].split())
            predicted = " ".join(output["text"].split())
            row = {"row": sample["row"], "image_sha256": sample["sha256"],
                   "reference_sha256": digest(expected.encode()), "predicted": predicted,
                   "reference_characters": len(expected), "reference_words": len(expected.split()),
                   "character_edits": edit_distance(expected, predicted),
                   "word_edits": edit_distance(expected.split(), predicted.split()),
                   "exact_line_match": expected == predicted, "inference_ms": output["elapsed"]}
            with raw_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            records.append(row)
        print(f"Evaluated {len(records)}/{len(samples)} lines ({time.monotonic()-started:.0f}s this session)", flush=True)

    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        assert page.evaluate("digitLab.applicationVersion") == protocol["application_version"]
        page.evaluate(HARNESS)
        # Warm each persistent worker serially, reusing downloaded model assets.
        for lane in (0, 1):
            if not remaining:
                break
            sample = remaining.pop(0)
            output = page.evaluate("async ({lane,job}) => ocrPredict(lane,job)", {"lane": lane, "job": payload(sample)})
            record([output])
        for index in range(0, len(remaining), 20):
            jobs = [payload(sample) for sample in remaining[index:index + 20]]
            record(page.evaluate("jobs => ocrBatch(jobs)", jobs))
        browser.close()
    assert len(records) == protocol["count"] and len({row["row"] for row in records}) == len(records)
    characters = sum(row["reference_characters"] for row in records)
    words = sum(row["reference_words"] for row in records)
    character_edits = sum(row["character_edits"] for row in records)
    word_edits = sum(row["word_edits"] for row in records)
    exact = sum(row["exact_line_match"] for row in records)
    report = {"status": "PASS", "completed_at": datetime.now(timezone.utc).isoformat(),
              "protocol": protocol_path.name, "protocol_sha256": digest(protocol_path.read_bytes()),
              "raw_predictions": raw_path.name, "raw_sha256": digest(raw_path.read_bytes()),
              "application_version": protocol["application_version"], "model": protocol["model"],
              "model_revision": protocol["model_revision"], "profile": "precise", "precision": "float32",
              "dataset": DATASET, "dataset_revision": REVISION, "split": "test", "lines": len(records),
              "reference_words": words, "reference_characters": characters,
              "word_edits": word_edits, "character_edits": character_edits, "exact_line_matches": exact,
              "word_error_rate": word_edits / words, "word_accuracy": 1 - word_edits / words,
              "character_error_rate": character_edits / characters, "exact_line_accuracy": exact / len(records),
              "mean_inference_ms": sum(row["inference_ms"] for row in records) / len(records),
              "training_performed": False, "model_selection_performed": False,
              "note": "English line OCR; word accuracy is 1-WER, not the fraction of wholly correct lines or isolated word crops."}
    write_json(final_path, report)
    print(json.dumps(report, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="words-1000")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--url", default="http://127.0.0.1:8770/")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", args.name):
        raise SystemExit("Use a simple evaluation name")
    if args.prepare:
        prepare(args.name, args.count, args.seed)
    if args.run:
        run(args.name, args.url, args.resume)


if __name__ == "__main__":
    main()
