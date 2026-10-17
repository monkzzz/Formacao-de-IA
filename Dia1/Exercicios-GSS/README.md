# Exercícios GSS — Dia 1, módulos 1 e 2

Doze demonstrações Python provenientes de `PIEP-Portugal/formacao_gss`.
Os nomes seguem `dia1_modulo<N>_<ordem>_<nome_do_exercicio>.py`.

- [Módulo 1 — Machine Learning e redes neuronais](modulo1/README.md): seis exercícios.
- [Módulo 2 — Modelos de linguagem](modulo2/README.md): seis exercícios.

Esta pasta complementa os enunciados já existentes no Dia 1. As demonstrações
Python exigem preparação própria. O módulo 3 e os exercícios antigos não estão
incluídos. Os exercícios UCI de dígitos usam imagens 8×8 e são independentes do
projeto MNIST 28×28 do Dia 2.

## Windows e Linux

O [guia comum](../../PORTABILITY.md) prepara ambientes separados nos dois sistemas.
Em Linux, usar `bin/python` em vez de `Scripts/python.exe` e instalar Tk para as
janelas. Os comandos PowerShell seguintes continuam disponíveis para Windows.

## Preparar e executar

Python 3.10 ou superior, com Tk disponível para as janelas. Na raiz do repositório:

```powershell
Set-Location Dia1/Exercicios-GSS
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\modulo1\dia1_modulo1_01_paradigmas_aprendizagem.py
.\.venv\Scripts\python.exe .\modulo2\dia1_modulo2_01_tokens_ids.py
```

Escolher os restantes ficheiros nas pastas `modulo1/` e `modulo2/`, pela ordem
indicada nos respetivos índices. Conservar as pastas de apoio e recursos.

Os exercícios 02, 03 e 05 do módulo 1 descarregam o dataset UCI Optical Digits
na primeira execução e reutilizam `.cache/datasets/` nesta pasta. O exercício 05
usa PyTorch na CPU. A inferência por desenho não atualiza os pesos nem substitui
a avaliação formal; a seleção do checkpoint usa validação, separada do teste.
Os exercícios 01 e 04 usam dados sintéticos.

Para a visão computacional, instalar também as dependências opcionais e preparar
os modelos antes da aula (a primeira preparação exige internet):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-visao.txt
.\.venv\Scripts\python.exe .\modulo1\dia1_modulo1_06_visao_computacional_yolo.py --preparar
.\.venv\Scripts\python.exe .\modulo1\dia1_modulo1_06_visao_computacional_yolo.py
```

Os cinco modelos ficam em `.cache/yolo/models/`, fora do Git. A GUI usa imagens,
vídeo ou webcam; selecionar a webcam não a ativa. Os scores não são accuracy.
As fontes das imagens estão em [recursos/README.md](recursos/README.md).

## Módulo 2 e respostas gravadas

As gravações incluídas permitem executar as demonstrações sem LM Studio:

```powershell
$env:FORMACAO_LMSTUDIO_OFFLINE = "1"
.\.venv\Scripts\python.exe .\modulo2\dia1_modulo2_04_proximo_token.py
```

Para inferência ao vivo, retirar essa variável e iniciar o LM Studio em
`http://localhost:1234`. Os modelos usados nas gravações são
`amalia-9b-0626-dpo` (texto), `text-embedding-bge-m3` (embeddings) e
`zai-org/glm-4.6v-flash` (imagem). As gravações têm cobertura limitada aos
exemplos preparados e a interface identifica quando as utiliza.
Os exercícios 01, 02, 04, 05 e 06 aceitam `--gravar` para atualizar as gravações
com os modelos disponíveis. Os exercícios não treinam nem ajustam LLMs.

## Verificação

A partir desta pasta, os testes usam dados sintéticos, gravações e simulações:

```powershell
$env:MPLBACKEND = "Agg"
$env:FORMACAO_LMSTUDIO_OFFLINE = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
```

Para executar um exercício sem janelas, definir também
`$env:FORMACAO_ML_NO_PAUSE = "1"`. No exercício YOLO, esse modo faz inferência
real nas cinco tarefas e exige os modelos preparados. Depois da verificação,
remover `MPLBACKEND` e `FORMACAO_ML_NO_PAUSE` para regressar às janelas:

```powershell
Remove-Item Env:MPLBACKEND, Env:FORMACAO_ML_NO_PAUSE -ErrorAction SilentlyContinue
```

## Proveniência

O [manifesto](origem.json) regista o commit de origem, os caminhos originais e
os hashes SHA-256 antes/depois da cópia. Os scripts de entrada e os recursos
conservam os bytes originais. As adaptações de código limitam-se aos caminhos
da cache, dos recursos e dos testes, para esta pasta funcionar autonomamente.
As dependências base declaram também Pillow, importado diretamente pelas GUIs.

Materiais de Hugo Gomes e Vinicius Canonici. Aplicam-se a
[licença do repositório](../../LICENSE.md) e as condições dos recursos de terceiros.
