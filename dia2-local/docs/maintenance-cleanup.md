# Website maintenance cleanup

This completes the five cleanup areas following the Python cleanup commit
`6d21ce5` and the [first frontend cleanup](frontend-cleanup.md). Changes are local;
there is no publication or new model-accuracy claim.

## Resulting organization and behavior

1. Submission HTML, CSS and JavaScript are expanded into readable source. Model
   loading commits a selection only after weight and evaluation identities match.
   A failed switch preserves the working model, records and controls; failed
   initial metadata loading has an explicit retry path. Busy controls prevent
   exporting or selecting old upload cards during a switch.
2. `dist/v3/browser-utils.js` supplies image decoding/validation, preview URL
   cleanup and downloads to both sites. Each site's original size/type/dimension
   policy is retained. Shared drawing tools own pointer isolation and undo/redo.
   Inference math, preprocessing contracts and trained weights are unchanged.
3. [The README](../README.md) now gives current setup and operating instructions.
   [Release history](release-history.md) preserves the former README with corrected
   relative links and labels its superseded statements explicitly. Scopedog's
   challenge answer now acknowledges the separate recorded supplementary follow-up
   and retains the warning that known-case follow-ups are not fresh blind tests.
4. [Browser QA](browser-qa.md) documents five maintained collectors sharing report
   and screenshot collision checks. Tests cover independent collisions, absolute
   report paths and invalid screenshot prefixes. The design collector also records
   an explicit overall status and prints its actual destination.
5. [The deployment map](deployment.md) distinguishes the full FTPS site from the
   restricted Pages package. Builds support separate names, QA selects a receipt,
   and archive/receipt collisions fail before any audit or site creation. The
   existing Pages workflow remains pinned to its reviewed v1 release.

## Executed validation

All 79 Python unit tests passed. Node parsed every current `dist/v3/` JavaScript
module and the submission entry module. Changed-source whitespace checks passed;
documentation link checks covered the README and new/updated guides and history.

| Local browser check | Result | Evidence |
| --- | --- | --- |
| Full-site CNN selection, 30 uploads and real activation/score parity | PASS, 19 groups | [Model report](../reports/maintenance-cleanup-v2-models.json) |
| Drawing, pointer isolation, word UI, cancellation, exports and parity | PASS, 18 groups; separate real OCR smoke NOT RUN | [Words report](../reports/maintenance-cleanup-v2-words.json) |
| Keyboard/layout/contrast/reduced motion | PASS, 6 groups | [Design report](../reports/maintenance-cleanup-v2-design-final.json) |
| Scopedog, correct challenge scope and safe text rendering | PASS, 6 groups | [Final helper report](../reports/maintenance-cleanup-v3-helper-qa.json) |
| Shared image I/O error paths and bitmap/URL release | PASS, 4 contracts with explicit bitmap doubles | [Resource report](../reports/maintenance-cleanup-v2-browser-io.json) |
| Final restricted package: four models, 40 uploads, metadata retry, model-switch failure recovery and mobile layout | PASS | [Package browser report](../reports/self-trained-submission-cleanup-v3-browser.json) |

The initial helper collector failure is retained in
[its own record](../reports/maintenance-cleanup-v2-helper-attempt1.json). The final
guide and collector preserve both historical-result scope and the blind-test
limitation. Earlier design/model/Words and intermediate package receipts remain
separate; none was overwritten to describe the final package.

The coding agent inspected desktop/mobile screenshots of the submission and the
full site's mobile view. Fresh Windows execution and independent human visual
review are NOT RUN. No official CAPTCHA inference, training, tuning, deployment,
release upload or remote website write occurred.

## Prepared package and preservation

Final local ZIP:
`artifacts/self-trained-submission-cleanup-v3/self-trained-submission-cleanup-v3.zip`.
The [build receipt](../reports/self-trained-submission-cleanup-v3-build.json)
identifies all 23 packaged files, four weight exports and the archive hash.
The extra file relative to v1 is the shared browser I/O module; no pretrained
reader or remote model loader is included.

The original v1 site still matches all 22 receipt hashes and its original ZIP
hash. Earlier packages and reports remain unchanged. GitHub Pages still uses its
pinned v1 package; the full site also needs a separate authorized deployment to
receive these local changes. The professor's all-ten confidence target remains
unmet, with no changes to recorded scores or evaluations.
