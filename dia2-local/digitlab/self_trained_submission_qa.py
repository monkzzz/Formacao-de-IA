"""Browser verification of the separate submission, with third-party access blocked."""

from functools import partial
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .letters import LetterCNN
from .model import DigitCNN
from .preprocess import prepare
from .qa import open_browser
from .qa_outputs import qa_outputs, qa_report
from .submission_artifacts import resolve_artifacts
from .residual import ResidualCNN
from .self_trained_submission import NAME, SPECS, digest
from .train import ROOT


def wait(page, expression, arg=None):
    """Poll via CDP evaluation without the CSP-sensitive string-eval waiter."""
    deadline = time.monotonic() + 60
    while not page.evaluate(expression, arg):
        if time.monotonic() > deadline:
            raise TimeoutError("Browser state did not settle: " + expression)
        page.wait_for_timeout(100)


def main(destination, receipt=None, screenshot_prefix=None, site=None, archive=None, artifact_root=None):
    receipt = Path(receipt) if receipt is not None else ROOT / "reports" / (NAME + "-build.json")
    build = json.loads(receipt.read_text(encoding="utf-8"))
    destination, captures = qa_outputs(destination, screenshot_prefix or build["name"])
    output, archive = resolve_artifacts(build, site=site, archive=archive, artifact_root=artifact_root)
    report = {"status": "FAIL", "build_sha256": digest(receipt),
              "artifacts": {"site": str(output), "archive": str(archive)},
              "checks": {}, "official_captcha_inference": "NOT RUN", "deployment": "NOT RUN"}
    with qa_report(destination, report):
        if any(digest(output / p) != value for p,value in build["files_sha256"].items()):
            raise ValueError("Frozen submission files changed")
        if digest(archive) != build["archive_sha256"]:
            raise ValueError("Frozen submission ZIP changed")
        torch.set_num_threads(2)

        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(output)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = open_browser(playwright)
                page = browser.new_page(viewport={"width": 1440, "height": 1100})
                requests, blocked, errors = [], [], []
                url = f"http://127.0.0.1:{server.server_port}/"
                def route(request):
                    if request.request.url.startswith((url, "blob:", "data:")):
                        request.continue_()
                    else:
                        blocked.append(request.request.url)
                        request.abort()
                page.route("**/*", route)
                page.on("request", lambda r: requests.append({"url": r.url, "method": r.method}))
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(url)
                wait(page,"Boolean(window.submission?.state.ready)")
                assert page.locator('#dataset').input_value() == 'mnist'
                assert page.locator('#mode option').all_text_contents() == ['Digits 0–9', 'Letters A–Z · EMNIST extension']
                assert page.locator('script[src]').count() == 1
                report['checks']['own_trained_options_and_mnist_default'] = 'PASS'
                for name,spec in SPECS.items():
                    mode = 'letters' if name == 'letters' else 'digits'
                    awaitable = page.evaluate("o=>submission.activate(o.mode,o.dataset)", {"mode":mode,"dataset":'mnist' if name == 'letters' else name})
                    manifest = json.loads((output / spec['folder'] / 'manifest.json').read_text())
                    assert page.evaluate('submission.state.model.manifest.sha256') == manifest['sha256']
                    fixture = json.loads((output / spec['folder'] / 'parity.json').read_text())
                    parity = page.evaluate("f=>f.cases.map(c=>{const r=submission.predict(c.input),delta=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));return {logits:delta(r.logits,c.logits),first:delta(r.first,c.pool1),second:delta(r.second,c.pool2),hidden:delta(r.hidden,c.hidden)};})", fixture)
                    assert all(v <= 1e-4 for row in parity for v in row.values())
                    network = LetterCNN() if name == 'letters' else ResidualCNN() if name == 'captcha-v3' else DigitCNN()
                    network.load_state_dict(torch.load(ROOT / spec['checkpoint'],map_location='cpu',weights_only=True))
                    network.eval()
                    paths = sorted((ROOT / 'reports' / ('letter-fixtures' if name == 'letters' else 'mnist-fixtures')).glob('*.png'))[:10]
                    page.locator('#files').set_input_files([str(p) for p in paths])
                    wait(page,'n=>!submission.state.busy&&submission.state.records.length===n',arg=len(paths))
                    records = page.evaluate('submission.exportRecord().predictions')
                    maximum = 0.
                    for path,row in zip(paths,records):
                        assert row['file'] == path.name and 'error' not in row
                        x = prepare(np.asarray(Image.open(path).convert('RGBA')),64 if name == 'captcha-v3' else 28)
                        np.testing.assert_allclose(x.flatten(),row['input'],atol=1e-6,rtol=0)
                        with torch.no_grad(): scores = network(torch.from_numpy(x[None])).softmax(1).numpy()[0]
                        error = float(np.max(np.abs(scores-row['scores'])))
                        maximum=max(maximum,error)
                        assert error<1e-5 and int(scores.argmax())==row['predicted']
                    assert page.locator('#first canvas').count()==16 and page.locator('#second canvas').count()==32
                    report['checks'][name] = {'status':'PASS','parity_cases':len(parity),'upload_count':len(paths),'maximum_score_error':maximum,'activation_errors':parity}
                # Same pixels under misleading filenames must produce the same output.
                page.evaluate("()=>submission.activate('digits','mnist')")
                source=(ROOT/'reports/mnist-fixtures/digit-1.png').read_bytes()
                page.locator('#files').set_input_files([{'name':'digit-9.png','mimeType':'image/png','buffer':source},{'name':'unrelated.png','mimeType':'image/png','buffer':source}])
                wait(page,'!submission.state.busy&&submission.state.records.length===2')
                records=page.evaluate('submission.exportRecord().predictions')
                assert records[0]['scores']==records[1]['scores']
                with page.expect_download() as download:
                    page.locator('#export').click()
                saved=download.value.path()
                exported=json.loads(saved.read_text())
                assert exported['predictions']==records and exported['labels_consulted_by_app'] is False
                report['checks']['filename_independence_and_raw_download']='PASS'
                page.locator('#files').set_input_files({'name':'invalid.txt','mimeType':'text/plain','buffer':b'not an image'})
                wait(page,'!submission.state.busy&&submission.state.records.length===3')
                assert 'error' in page.evaluate('submission.state.records[2]')
                page.locator('#clear').click();page.locator('#read').click()
                assert 'No visible digit' in page.locator('#status').inner_text()
                canvas=page.locator('#drawing');box=canvas.bounding_box()
                page.mouse.move(box['x']+box['width']/2,box['y']+35);page.mouse.down();page.mouse.move(box['x']+box['width']/2,box['y']+220,steps=10);page.mouse.up()
                drawn=canvas.evaluate('c=>Array.from(c.getContext("2d").getImageData(0,0,c.width,c.height).data)')
                page.locator('#drawing-undo').click()
                undone=canvas.evaluate('c=>Array.from(c.getContext("2d").getImageData(0,0,c.width,c.height).data)')
                assert drawn!=undone
                page.locator('#drawing-redo').click()
                assert drawn==canvas.evaluate('c=>Array.from(c.getContext("2d").getImageData(0,0,c.width,c.height).data)')
                page.locator('#read').click()
                assert page.locator('#prediction').inner_text()!='—'
                # Loaded inference remains available with every subsequent request blocked.
                page.route('**/*',lambda route:route.abort())
                assert len(page.evaluate('submission.predict(submission.state.current.input).scores'))==10
                report['checks']['drawing_undo_redo_blank_invalid_and_loaded_offline_inference']='PASS'
                try:
                    page.evaluate("()=>submission.activate('words','mnist')")
                    raise AssertionError('Forbidden pretrained mode accepted')
                except Exception as error:
                    assert 'Unsupported submission model' in str(error)
                report['checks']['pretrained_mode_refused']='PASS'
                if 'v3/browser-utils.js' in build['files_sha256']:
                    retry = browser.new_page()
                    retry.route('**/*', route)
                    retry.on('request', lambda r: requests.append({'url':r.url,'method':r.method}))
                    retry.on('pageerror', lambda e: errors.append(str(e)))
                    retry.route('**/evaluation.json', lambda r: r.fulfill(status=503, body='unavailable'))
                    retry.goto(url)
                    wait(retry, 'Boolean(window.submission)&&!submission.state.busy')
                    assert not retry.evaluate('submission.state.ready')
                    assert retry.locator('#retry').is_visible()
                    assert retry.locator('#read').is_disabled()
                    retry.unroute('**/evaluation.json')
                    retry.locator('#retry').click()
                    wait(retry, 'submission.state.ready&&!submission.state.busy')
                    retry.locator('#files').set_input_files(str(ROOT/'reports/mnist-fixtures/digit-1.png'))
                    wait(retry, 'submission.state.records.length===1&&!submission.state.busy')
                    original_records = retry.evaluate('submission.exportRecord().predictions')
                    original_hash = retry.evaluate('submission.state.model.manifest.sha256')
                    pending = []
                    retry.route('**/model/captcha-v3/digits/manifest.json*', lambda r: pending.append(r))
                    retry.locator('#dataset').select_option('captcha-v3')
                    wait(retry, 'submission.state.busy')
                    assert retry.locator('#export').is_disabled()
                    assert retry.locator('#uploads button').first.is_disabled()
                    deadline = time.monotonic() + 10
                    while not pending:
                        if time.monotonic() > deadline:
                            raise TimeoutError('Expected model request was not made')
                        retry.wait_for_timeout(50)
                    pending[0].fulfill(status=503, body='unavailable')
                    wait(retry, '!submission.state.busy')
                    assert retry.evaluate('submission.state.ready')
                    assert retry.locator('#dataset').input_value() == 'mnist'
                    assert retry.evaluate('submission.state.model.manifest.sha256') == original_hash
                    assert retry.evaluate('submission.exportRecord().predictions') == original_records
                    assert retry.locator('#export').is_enabled()
                    retry.close()
                    report['checks']['metadata_retry_model_failure_recovery_and_busy_controls']='PASS'
                page.screenshot(path=str(captures['desktop']),full_page=True)
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.screenshot(path=str(captures['mobile']),full_page=True)
                assert not blocked and not errors and all(r['method']=='GET' and r['url'].startswith((url,'blob:','data:')) for r in requests)
                assert all(digest(ROOT / p)==value for p,value in build['active_assets_preserved'].items())
                report.update(status='PASS',requests=requests,blocked_external_requests=blocked,page_errors=errors,
                              active_assets_preserved=True,browser_version=browser.version,
                              visual_manual_review='NOT RUN; screenshots captured')
                browser.close()
        finally:
            server.shutdown();server.server_close()
        print('PASS: three models, 30 uploads, activations, drawing/export/mobile and no external network requests')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'reports'/(NAME+'-browser.json'))
    parser.add_argument('--build',type=Path,help='Build receipt for a separately named package')
    parser.add_argument('--screenshot-prefix')
    parser.add_argument('--site', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--artifact-root', type=Path)
    args=parser.parse_args()
    main(args.report,args.build,args.screenshot_prefix,args.site,args.archive,args.artifact_root)
