# Official follow-up: fixed weights with small-component cleanup

Explicit user-requested official follow-up after prior exposure; reserved independent test still NOT RUN; never training, tuning or model selection.

| Preparation | Correct / 10 | Correct with score strictly >90% / 10 |
| --- | ---: | ---: |
| Preserved current preparation (earlier frozen result) | 10 | 6 |
| Selected cleanup preparation (new frozen follow-up) | 9 | 6 |

Professor acceptance (10/10 correct, every score strictly >90%): **False**.

| File | Expected | Previous prediction / top score | Cleanup prediction / top score | Correct |
| --- | ---: | --- | --- | --- |
| caso_01.png | 8 | 8 / 99.26% | 8 / 99.42% | True |
| caso_02.png | 3 | 3 / 95.31% | 3 / 97.67% | True |
| caso_03.png | 0 | 0 / 99.76% | 0 / 99.50% | True |
| caso_04.png | 6 | 6 / 72.22% | 6 / 80.15% | True |
| caso_05.png | 1 | 1 / 58.14% | 1 / 51.79% | True |
| caso_06.png | 9 | 9 / 99.76% | 9 / 99.87% | True |
| caso_07.png | 4 | 4 / 76.93% | 4 / 81.70% | True |
| caso_08.png | 2 | 2 / 95.37% | 2 / 95.60% | True |
| caso_09.png | 7 | 7 / 98.50% | 7 / 98.46% | True |
| caso_10.png | 5 | 5 / 55.56% | 3 / 71.19% | False |

[Freeze](fixed-weight-preprocessing-v1-challenge-freeze.json) · [Raw predictions](fixed-weight-preprocessing-v1-challenge-raw.json) · [Strict comparison](fixed-weight-preprocessing-v1-challenge-comparison.json).

Weights are identical; only the already development-selected preparation differs. The comparison uses saved raw outputs, not score rescaling or label-derived inference. The independent reserved test is NOT RUN: this was an explicit request for an early official follow-up, not a claim that final independent gates were passed. No active application change, training, model selection, publication or push followed. Historical records remain preserved. Do not use this exposed outcome to choose another transform or parameter.
