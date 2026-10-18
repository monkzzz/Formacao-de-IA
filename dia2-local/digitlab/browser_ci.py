"""Check current frontend sources against reviewed weights, without training or official inputs."""

import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.request import urlopen
import zipfile

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .letters import LetterCNN
from .model import DigitCNN
from .preprocess import prepare
from .qa import open_browser
from .qa_outputs import qa_outputs, qa_report
from .residual import ResidualCNN
from .self_trained_pages_qa import wait
from .train import ROOT

DEFAULT_RECEIPT = ROOT / "reports/self-trained-submission-cleanup-v4-build.json"
MODELS = {"mnist": "model", "mnist-supplementary-v1": "model/mnist-supplementary-v1/digits",
          "captcha-v3": "model/captcha-v3/digits", "letters": "model/robust/letters"}


def reviewed_payloads(archive, receipt):
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest() != receipt["archive_sha256"]:
        raise ValueError("Reviewed archive hash mismatch")
    with zipfile.ZipFile(archive) as bundle:
        expected = receipt["files_sha256"]
        if len(bundle.namelist()) != len(expected) or set(bundle.namelist()) != set(expected):
            raise ValueError("Unexpected or duplicate archive entries")
        payloads = {}
        for name, checksum in expected.items():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError("Unsafe archive path")
            if bundle.getinfo(name).file_size > 20 * 1024 * 1024:
                raise ValueError("Oversized archive entry")
            data = bundle.read(name)
            if hashlib.sha256(data).hexdigest() != checksum:
                raise ValueError("Reviewed asset hash mismatch")
            payloads[name] = data
        return payloads


def native_model(site, name):
    folder = site / MODELS[name]
    manifest = json.loads((folder / "manifest.json").read_text())
    data = (folder / "weights.bin").read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["sha256"] or len(data) != manifest["bytes"]:
        raise ValueError("Invalid reviewed weights")
    model = LetterCNN() if name == "letters" else ResidualCNN() if name == "captcha-v3" else DigitCNN()
    state, cursor = {}, 0
    expected = model.state_dict()
    for item in manifest["tensors"]:
        key = item["name"]
        if key in state or key not in expected or item["offset"] != cursor or list(expected[key].shape) != item["shape"] or expected[key].numel() != item["length"]:
            raise ValueError("Invalid reviewed tensor layout")
        state[key] = torch.from_numpy(np.frombuffer(data, dtype="<f4", offset=cursor * 4,
                                                   count=item["length"]).copy().reshape(item["shape"]))
        cursor += item["length"]
    if cursor * 4 != len(data) or set(state) != set(expected):
        raise ValueError("Incomplete reviewed tensor layout")
    model.load_state_dict(state)
    return model.eval(), manifest


def prepare_weights(payloads, root=ROOT):
    """Restore reviewed ignored binaries/parity fixtures; preserve checkout manifests."""
    restored = []
    for folder in MODELS.values():
        name = folder + "/weights.bin"
        payload = payloads[name]
        checksum = hashlib.sha256(payload).hexdigest()
        manifest = json.loads((root / "dist" / folder / "manifest.json").read_text())
        if checksum != manifest["sha256"] or len(payload) != manifest["bytes"]:
            raise ValueError("Reviewed weights differ from checkout manifest: " + folder)
        parity_name = folder + "/parity.json"
        parity = payloads[parity_name]
        if json.loads(parity)["model_sha256"] != checksum:
            raise ValueError("Reviewed parity fixture/model mismatch: " + folder)
        for relative, content in ((name, payload), (parity_name, parity)):
            path = root / "dist" / relative
            if path.exists():
                if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(content).digest():
                    raise ValueError("Preserve differing existing model asset: " + relative)
            else:
                with path.open("xb") as stream:
                    stream.write(content)
                restored.append(relative)
    return restored


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(site):
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--archive", type=Path, help="Use a local reviewed ZIP instead of downloading its release")
    parser.add_argument("--report", default="browser-ci.json")
    parser.add_argument("--prefix", default="browser-ci")
    parser.add_argument("--prepare-only", action="store_true", help="Restore missing reviewed binaries before clean-checkout unit tests")
    args = parser.parse_args()
    destination, captures = qa_outputs(args.report, args.prefix, ("full", "submission"))
    # Preflight subprocess destinations as well: failed CI evidence is never replaced.
    for suffix in ("design", "words", "readers"):
        names = ("390", "1440") if suffix == "design" else ("desktop", "mobile")
        qa_outputs(args.prefix + "-" + suffix + ".json", args.prefix + "-" + suffix, names)
    qa_outputs(args.prefix + "-helper-qa.json", args.prefix + "-helper")
    report = {"checks": {}, "scope": "Current checkout UI with four reviewed participant-trained exports; no training, official images, external OCR downloads or deployment"}
    torch.set_num_threads(2)
    with qa_report(destination, report), tempfile.TemporaryDirectory(prefix="digitlab-ci-") as temporary:
        work = Path(temporary)
        receipt = json.loads(args.receipt.read_text())
        archive = args.archive
        if archive is None:
            archive = work / "reviewed.zip"
            name = receipt["name"]
            if not name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-" for c in name):
                raise ValueError("Unsafe release identity")
            url = f"https://github.com/monkzzz/Formacao-de-IA/releases/download/{name}/{name}.zip"
            with urlopen(url, timeout=120) as response, archive.open("xb") as stream:
                shutil.copyfileobj(response, stream)
        payloads = reviewed_payloads(archive, receipt)
        if args.prepare_only:
            report["checks"]["reviewed_weights"] = {"status": "PASS", "restored": prepare_weights(payloads)}
            return
        full, submission = work / "full", work / "submission"
        shutil.copytree(ROOT / "dist", full, ignore=shutil.ignore_patterns("model", "roms"))
        for name, data in payloads.items():
            target = submission / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if name.startswith("model/"):
                target = full / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        for source, target in ((ROOT / "submission/index.html", submission / "index.html"),
                               (ROOT / "submission/submission.js", submission / "submission.js"),
                               (ROOT / "submission/submission.css", submission / "submission.css")):
            shutil.copy2(source, target)
        for name in payloads:
            if name.startswith("v3/"):
                shutil.copy2(ROOT / "dist" / name, submission / name)
        report["archive_sha256"] = receipt["archive_sha256"]
        report["checks"]["reviewed_weights_current_frontends"] = "PASS"
        servers = []
        try:
            with sync_playwright() as playwright:
                browser = open_browser(playwright)
                report["browser_version"] = browser.version
                for variant, site in (("full", full), ("submission", submission)):
                    server, url = serve(site)
                    servers.append(server)
                    context = browser.new_context(viewport={"width": 1440, "height": 1100})
                    blocked, errors = [], []
                    def guard(route):
                        request = route.request
                        if request.method == "GET" and request.url.startswith((url, "blob:", "data:")):
                            route.continue_()
                        else:
                            blocked.append(request.url)
                            route.abort()
                    context.route("**/*", guard)
                    page = context.new_page()
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(url)
                    if variant == "full":
                        full_url = url
                        page.wait_for_function("window.digitLab?.state.ready")
                        assert page.locator("#cnn-model").input_value() == "mnist"
                    else:
                        wait(page, "Boolean(window.submission?.state.ready)")
                        assert page.locator("#dataset").input_value() == "mnist"
                    for name in MODELS:
                        mode = "letters" if name == "letters" else "digits"
                        if variant == "full":
                            page.evaluate("async x=>await digitLab.activateMode(x.mode,x.name)", {"mode": mode, "name": "mnist" if mode == "letters" else name})
                            expression = "digitLab"
                        else:
                            page.evaluate("async x=>await submission.activate(x.mode,x.name)", {"mode": mode, "name": "mnist" if mode == "letters" else name})
                            expression = "submission"
                        fixture = json.loads((site / MODELS[name] / "parity.json").read_text())
                        parity = page.evaluate("""({fixture, app})=>fixture.cases.map(c=>{
                          const r=window[app].predict(c.input),delta=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));
                          return Math.max(delta(r.logits,c.logits),delta(r.hidden,c.hidden),delta(r.first,c.pool1),delta(r.second,c.pool2));
                        })""", {"fixture": fixture, "app": expression})
                        assert max(parity) < 1e-4
                        model, manifest = native_model(site, name)
                        image = ROOT / "reports" / ("letter-fixtures/letter-A.png" if mode == "letters" else "mnist-fixtures/digit-1.png")
                        before = page.evaluate(expression + ".exportRecord().predictions.length")
                        page.locator("#files").set_input_files(str(image))
                        wait(page, "x=>!window[x.app].state.busy&&window[x.app].exportRecord().predictions.length===x.count", {"app": expression, "count": before + 1})
                        row = page.evaluate(expression + ".exportRecord().predictions.at(-1)")
                        assert not row.get("error") and row["model_sha256"] == manifest["sha256"]
                        pixels = prepare(np.asarray(Image.open(image).convert("RGBA")), 64 if name == "captcha-v3" else 28)
                        with torch.no_grad():
                            expected = model(torch.from_numpy(pixels[None])).softmax(1).numpy()[0]
                        np.testing.assert_allclose(row["input"], pixels.flatten(), atol=1e-6, rtol=0)
                        np.testing.assert_allclose(row["scores"], expected, atol=1e-5, rtol=0)
                        report["checks"][variant + "-" + name] = {"status": "PASS", "parity_cases": len(parity), "upload_native_score_error": float(np.max(np.abs(expected-row["scores"]))) }
                    with page.expect_download():
                        page.locator("#export").click()
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
                    page.screenshot(path=str(captures[variant]), full_page=True)
                    assert not blocked and not errors
                    report["checks"][variant + "-export-mobile-local-only"] = "PASS"
                    context.close()
                browser.close()
            for module, suffix in (("design_qa", "design"), ("helper_qa", "helper"), ("words_qa", "words"), ("digit_readers_qa", "readers")):
                command = [sys.executable, "-m", "digitlab." + module, "--url", full_url]
                prefix = args.prefix + "-" + suffix
                if suffix == "helper":
                    command += ["--report-prefix", prefix]
                else:
                    command += ["--report", prefix + ".json", "--screenshot-prefix", prefix]
                if suffix in ("words", "readers"):
                    command += ["--digit-experiment", "mnist"]
                subprocess.run(command, cwd=ROOT, check=True)
                report["checks"][module] = "PASS"
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
    print(json.dumps({"status": report["status"], "checks": len(report["checks"])}))


if __name__ == "__main__":
    main()
