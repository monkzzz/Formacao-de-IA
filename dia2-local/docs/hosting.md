# Website Hosting

Public URL: https://naoquerosaber.pt/AI/index.html

Static application assets and both trained models are served by the hosting account. Inference remains in the browser; no Python service is deployed. Use HTTPS because the model-integrity and upload-record APIs use secure browser capabilities.

## Current robustness release

The public app now loads the improved digit and letter models from
`model/robust/digits/` and `model/robust/letters/`. All 22 uploaded assets passed
SHA-256 verification by downloading them over FTPS. Replaced files were backed
up locally; unrelated remote files were retained. See the
[deployment record](../reports/ftp-deployment.json).

[Public browser verification](../reports/public-robust-browser-qa.json) passed
for both selected model identities, all 36 classes, activation parity against
Python, image uploads, mixed-mode records, invalid inputs, mobile layout and
recovery from a failed model download. Inference remains entirely in-browser.
The original digit and letter exports are retained for older cached releases.

The verification commands below describe the earlier original-model releases.
Use `digitlab.robust_qa` for the current models. Its default report target is
`reports/robust-browser-qa.json`; the public run was saved separately to
`reports/public-robust-browser-qa.json` to preserve local evidence.

## Credentials and directory mapping

Copy the structure in `ftp.example.json` into the ignored `ftp.local.json`. Never commit real credentials. FTPS verifies the server certificate; `tls_hostname` can identify the provider's canonical certificate hostname when it resolves to the same server as the configured host.

The current FTP login directory maps directly to the public `/AI/` directory. Its configuration uses `remote_dir: "/"` and `allow_ftp_root: true`. Do not create another `AI` folder inside it. Recheck this mapping if the FTP account changes.

## Check and deploy

From the project directory:

```powershell
python -m digitlab.ftp_deploy
python -m digitlab.ftp_verify
python -m digitlab.ftp_deploy --upload
.\.venv\Scripts\python.exe -m digitlab.public_qa
.\.venv\Scripts\python.exe -m digitlab.letters_qa --url https://naoquerosaber.pt/AI/ --public
```

The first two commands are read-only. Upload backs up existing files to ignored local artifacts, transfers the application assets, and downloads each uploaded file to verify its SHA-256. It does not delete unrelated remote files. Versioned `v2/` assets and both model directories are uploaded before `index.html` is switched; original root assets remain available for cached v1 pages.

The current design uses `v3/` assets and retains both older versions for cached pages. Verify it with:

```powershell
.\.venv\Scripts\python.exe -m digitlab.design_qa --url https://naoquerosaber.pt/AI/ --public
.\.venv\Scripts\python.exe -m digitlab.public_qa --report public-design-digits-qa.json
.\.venv\Scripts\python.exe -m digitlab.letters_qa --url https://naoquerosaber.pt/AI/ --public --report public-design-letters-qa.json
```

All 25 groups passed for the design release. Earlier report names remain evidence for their own releases rather than being overwritten.

Public QA uses clean handwriting and synthetic fixtures, keeping original local reports and screenshots separate. The historical digit-only result is in `reports/public-browser-qa.json`; new digit and letter results use `reports/public-browser-qa-v2.json` and `reports/public-letters-browser-qa.json` respectively. These checks do not train or tune either model.

Earlier hosting diagnostic reports document genuine 404 and verification-page failures before the directory mapping was corrected. They are historical evidence, not the current public-site status. The trained weights and original challenge record were not changed by deployment.
