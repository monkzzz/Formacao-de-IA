# Desafio oficial — 10 dígitos problemáticos em estilo CAPTCHA

**Este é o único conjunto oficial de imagens do desafio final do Dia 2.**

Os **dez arquivos `caso_01.png` a `caso_10.png` estão diretamente nesta pasta**, sem subdiretório. São dez imagens PNG de **192 × 192 pixels**, com um exemplo de cada dígito de **0 a 9**.

## Arquivos

**[Acessar a pasta dos dez PNGs](./)**

Para testar, baixe os arquivos `caso_01.png` a `caso_10.png` e carregue-os pelo **upload da aplicação GitHub Pages** desenvolvida no Exercício 3. Não é necessário executar o código gerador.

## Por que são difíceis?

Ao contrário do MNIST, que possui caracteres isolados e relativamente limpos, os exemplos deste desafio combinam:

- **Linhas sinuosas cruzando o dígito**, com cor e espessura semelhantes à tinta do caractere.
- **Traços interrompidos e oclusões**, que removem partes da forma original.
- **Fragmentos de tinta e riscos dispersos**, que atrapalham recorte e separação entre fundo e símbolo.
- **Deformações locais, inclinações e diferenças de caligrafia**, que alteram a geometria.
- **Textura, contraste variável e ruído**, dificultando a normalização da imagem.

As perturbações estão nos **pixels das imagens**. Um arquivo com nome neutro não é, por si só, um CAPTCHA: o problema que a rede precisa resolver é visual.

## Como avaliar corretamente

1. Treinar o modelo com o [MNIST](../Dataset-MNIST/README.md), separando treino, validação e teste sem vazamento.
2. Registrar **a versão do modelo e do site antes de abrir as imagens do desafio** para classificação.
3. No site publicado, fazer upload **dos dez PNGs** e registrar as dez previsões, pontuações e evidências.
4. **Só depois** comparar com o gabarito e contabilizar os acertos, idealmente com o professor.
5. Investigar se cada erro vem da rede, da segmentação, do tratamento das cores ou da inferência no navegador.
6. Reportar separadamente a **acurácia nos 10.000 exemplos oficiais de teste do MNIST** e os **acertos nas dez imagens CAPTCHA**.

Os rótulos não constam dos nomes dos PNGs, mas podem ser descobertos no código gerador; **não consulte o gerador como gabarito antes de registrar as previsões**.

**Não existe garantia de que a rede errará todas as imagens.** Alguns dígitos também podem parecer ambíguos para seres humanos. O objetivo é demonstrar robustez, reconhecer limites e produzir evidências verificáveis, não prometer uma taxa de acerto.

## Resultado de referência do professor

Uma execução automatizada pelo upload do [Image-classifier-demo](https://vcanonici.github.io/Image-classifier-demo/) registrou **3 acertos em 10 casos (30%)**, com **7 erros**, para a versão do modelo naquele teste.

**[Execução, logs e relatório do teste de referência](https://github.com/vcanonici/Formacao-de-IA/actions/runs/38550708626)**.

Esse resultado não é uma meta para os alunos, nem representa o desempenho garantido de outra rede. Faça primeiro suas previsões independentes.

## Recursos

### Maintenance automation (2026-10-17)

The ten PNGs in this directory remain reserved for final evaluation. The generator
defaults to `Avancado/` as a **separate output for generator auditing**, not another
official challenge or training data. The same algorithm and classes do not create
an independent benchmark. Never replace official PNGs. The output directory must
be empty; `--output-dir Dia2/Desafio` is refused.

```powershell
python -m pip install Pillow==11.3.0
python Dia2/Desafio/gerar_desafio_avancado.py --output-dir <pasta-vazia>
```

The fonts `DejaVuSans-Bold.ttf` and `DejaVuSerif-BoldItalic.ttf` are required.
The generation workflow saves a temporary artifact without committing, pushing
or changing official images. Exact reproducibility also depends on Pillow and
font versions.

The [evaluator](avaliar_captcha_no_site.py) supports the Digit Lab interface
(`window.digitLab`, `#files`, `#app-version`), rather than arbitrary classifiers.
It collects real predictions and hashes through upload without reading labels or
computing accuracy. It requires Playwright 1.55.0 and Chromium:

```powershell
python -m pip install playwright==1.55.0
python -m playwright install chromium
python Dia2/Desafio/avaliar_captcha_no_site.py --url <url-digit-lab> --input-dir <pasta-png> --output <novo-relatorio.json>
```

Official PNGs require `--allow-official-followup`. Evaluation is manual-only and
requires a URL and explicit follow-up confirmation. Never tune from known outcomes.
Loading, contract or inference failures produce `FAIL`, a nonzero exit status and
diagnostic JSON; the workflow attempts to retain reports even on failure. Errors
before evaluator startup, such as browser installation failures, may produce no
JSON. Existing reports are never overwritten.

- [Exercício 3 · Parte 4 — Teste do desafio](../Exercicio-03/Parte-04-Teste-do-Desafio.md)
- [Gerador auditável das dez imagens](gerar_desafio_avancado.py)
- [Aplicação de referência com upload](https://vcanonici.github.io/Image-classifier-demo/)
