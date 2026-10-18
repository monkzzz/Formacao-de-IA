"""Verify the published participant-trained Pages site using non-challenge fixtures."""

import argparse
import json
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
from .residual import ResidualCNN
from .self_trained_submission import NAME, SPECS, digest
from .train import ROOT, write_json


def wait(page, expression, arg=None):
    """Poll via CDP evaluation without the CSP-sensitive string-eval waiter."""
    deadline = time.monotonic() + 60
    while not page.evaluate(expression, arg):
        if time.monotonic() > deadline:
            raise TimeoutError("Browser state did not settle: " + expression)
        page.wait_for_timeout(100)


def main(destination, url):
    if destination.exists():
        raise FileExistsError("Preserve completed browser verification")
    build = json.loads((ROOT / "reports" / (NAME + "-build.json")).read_text())
    output = Path(build["output"])
    if any(digest(output / p) != value for p,value in build["files_sha256"].items()):
        raise ValueError("Frozen submission files changed")
    if digest(Path(build["archive"])) != build["archive_sha256"]:
        raise ValueError("Frozen submission ZIP changed")
    report = {"status": "FAIL", "build_sha256": digest(ROOT / "reports" / (NAME + "-build.json")),
              "checks": {}, "official_captcha_inference": "NOT RUN", "scope": "Public deployment verification with non-challenge fixtures"}
    torch.set_num_threads(2)

    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            requests, blocked, errors = [], [], []
            report["url"] = url
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
                page.evaluate("o=>submission.activate(o.mode,o.dataset)", {"mode":mode,"dataset":'mnist' if name == 'letters' else name})
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
            folder=ROOT/'reports/screenshots';folder.mkdir(exist_ok=True)
            page.screenshot(path=str(folder/(NAME+'-pages-desktop.png')),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(folder/(NAME+'-pages-mobile.png')),full_page=True)
            assert not blocked and not errors and all(r['method']=='GET' and r['url'].startswith((url,'blob:','data:')) for r in requests)
            assert all(digest(ROOT / p)==value for p,value in build['active_assets_preserved'].items())
            report.update(status='PASS',requests=requests,blocked_external_requests=blocked,page_errors=errors,
                          active_assets_preserved=True,browser_version=browser.version,
                          visual_manual_review='NOT RUN; screenshots captured')
            browser.close()
    finally:
        write_json(destination,report)
    print('PASS: four models, 40 uploads, activations, drawing/export/mobile and no external network requests')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'reports'/'self-trained-pages-v1-browser.json')
    parser.add_argument('--url',default='https://monkzzz.github.io/Formacao-de-IA/')
    args=parser.parse_args()
    main(args.report,args.url)
