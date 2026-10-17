# Executar em Windows e Linux

Usar Python 3.12 de 64 bits para o ambiente comum dos dois dias. O script
[setup_course.py](setup_course.py) cria ambientes separados por sistema operativo
em `.runtime/`, sem substituir ambientes anteriores nem incluir dependências no Git.
Executar os comandos seguintes na raiz do repositório.

## Windows — PowerShell

```powershell
py -3.12 setup_course.py --component day1 --install
py -3.12 setup_course.py --component day2 --install --fonts --browser
```

Os executáveis ficam em `.runtime/windows/day1/Scripts/python.exe` e
`.runtime/windows/day2/Scripts/python.exe`. Usar diretamente o executável do dia
pretendido; não é necessário ativar o ambiente nem alterar a política de PowerShell.

## Linux — Bash

Instalar Python, suporte a `venv` e Tk através do gestor de pacotes da distribuição.
Em Debian/Ubuntu, os pacotes são `python3-venv` e `python3-tk`. Para executar janelas,
é necessária uma sessão gráfica. O Playwright também precisa das bibliotecas de
sistema do Chromium; se faltarem, executar o comando de instalação de dependências
indicado pelo próprio Playwright (`python -m playwright install-deps chromium`,
com as permissões de administração apropriadas).

```bash
python3 setup_course.py --component day1 --install
python3 setup_course.py --component day2 --install --fonts --browser
```

Os executáveis ficam em `.runtime/linux/day1/bin/python` e
`.runtime/linux/day2/bin/python`.

## Executar e verificar

Dia 1: entrar em `Dia1/Exercicios-GSS/` e usar o Python do ambiente correspondente
para executar `modulo2/dia1_modulo2_01_tokens_ids.py`. Para testes offline:

```bash
MPLBACKEND=Agg FORMACAO_LMSTUDIO_OFFLINE=1 ../../.runtime/linux/day1/bin/python -m unittest discover -s tests -t .
```

Em PowerShell, definir `$env:MPLBACKEND="Agg"` e
`$env:FORMACAO_LMSTUDIO_OFFLINE="1"`, usando
`../../.runtime/windows/day1/Scripts/python.exe` para o mesmo comando unittest.
YOLO continua opcional: instalar `requirements-visao.txt` no ambiente do Dia 1 e
seguir o [guia local](Dia1/Exercicios-GSS/README.md).

Dia 2: entrar em `dia2-local/` e executar com o Python do ambiente do Dia 2:

```text
<python> -m unittest discover -s tests -v
<python> serve.py
<python> -m digitlab.confidence_broad --stage train
```

Para um clone sem pesos, executar `<python> serve.py --download-models`, esperar
pela verificação dos downloads e terminar o servidor com Ctrl+C. Depois executar
`<python> -m digitlab.restore_checkpoint` para recuperar o checkpoint residual a
partir dos tensores verificados. O comando recusa substituir um checkpoint existente.
Os tensores são idênticos aos do modelo publicado; o hash do ficheiro PyTorch
serializado pode diferir do original. O processo não treina nem usa imagens do desafio.
Os downloads dependem da disponibilidade do host publicado e dos hashes no manifesto.
A recuperação não fornece checkpoints históricos diferentes nem os seus otimizadores.
As experiências também recusam sobrescrever destinos existentes.

## Fontes e navegador

O novo ensaio usa o mesmo conjunto aberto nos dois sistemas. O download fixa uma
revisão do repositório Google Fonts, verifica os hashes do
[manifesto](dia2-local/docs/confidence-fonts.json) e conserva as licenças de cada
família em `dia2-local/data/open-fonts/`, fora do Git. As famílias de treino,
desenvolvimento e teste são separadas. O ensaio regista versões e hashes reais;
resultados numericamente idênticos entre sistemas não são garantidos.

Os ensaios históricos conservam os nomes das fontes originais. A variável
`DIGITLAB_FONT_ROOT` permite indicar uma pasta de fontes licenciadas, pesquisada
recursivamente pelo nome exato. Não há substituição automática de fontes Windows
por fontes Linux. Nomes ausentes ou ambíguos produzem um erro explícito.

Os verificadores de navegador usam `DIGITLAB_BROWSER_EXECUTABLE`, quando definida;
caso contrário, procuram Chromium/Chrome/Edge instalados e depois o Chromium do
Playwright. A inferência continua no navegador.

O [workflow de verificação](.github/workflows/python-platforms.yml) prepara testes
em Windows e Linux. A sua existência não significa que já tenha sido executado
no GitHub; o relatório desta tarefa deve distinguir testes locais de CI.

Em Linux sem ecrã, `xvfb-run -a` permite executar também os quatro testes Tk da
visão computacional. Isso é uma verificação automatizada com ecrã virtual, não
interação manual num ambiente de trabalho. Ver [resultados locais e limites](dia2-local/reports/portability-validation.json).

Para incluir o novo ensaio de consistência/capacidade e os seus gráficos, acrescentar
`--confidence` à preparação do Dia 2: `python setup_course.py --component day2 --install --confidence --fonts --browser`.
O [protocolo](dia2-local/docs/confidence-suite.md) descreve os dados independentes,
os três braços de treino e as verificações no navegador.
