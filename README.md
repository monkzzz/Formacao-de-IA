<div align="center">

Guia de ambiente: [Windows e Linux](PORTABILITY.md).

# Formação de IA

### Da pesquisa com IA à engenharia de software com agentes

**Uma formação prática para aprender a investigar, construir, verificar e melhorar resultados com inteligência artificial.**

<br>

![Formação em 2 dias](https://img.shields.io/badge/FORMAÇÃO-2%20DIAS-192A56?style=for-the-badge)
![Dia 1 — Microsoft Copilot](https://img.shields.io/badge/DIA%201-MICROSOFT%20COPILOT-0078D4?style=for-the-badge)
![Dia 2 — GitHub Copilot](https://img.shields.io/badge/DIA%202-GITHUB%20COPILOT-6E40C9?style=for-the-badge)

**[Começar pelo Dia 1](Dia1/README.md)** · **[Explorar o Dia 2](Dia2/README.md)** · **[Apresentações](#apresentações-dos-módulos-pdf)** · **[Ver o desafio final](Dia2/Exercicio-03-Desenvolvimento-Issues.md)**

</div>

---

## A proposta

### Personal-fork navigation — 2026-10-17

This fork also contains the participant's work. Students should keep their own
implementations in their personal repositories; these additions are evidence and
reference material, not substitutes for completing the course exercises.

| Location | Role |
| --- | --- |
| [Participant work](participant-work/day1/README.md) | Day 1 research, reading notes, synthesis, audit and execution evidence |
| [Reusable starter](participant-work/starter/README.md) | Personal starter and bootstrap skill; separate evidence records describe actual tests |
| [Day 2 study answers](Dia2-Answers/README.md) | Explanations and proposed answers, separate from practical completion |
| [Digit Lab implementation](dia2-local/README.md) | Trained classifier and browser app, with versioned evidence and ignored model recovery |
| [Preparation proposal](DIA2-PROPOSTA.md) | Historical plan with a dated current-status pointer |
| [Task checklist](TASKS.md) | Completion evidence, maintenance work and external dependencies |
| [Current submission](participant-work/day2/submission-browser-delivery.md) | Existing public URL, default model identity and fresh browser checks |
| [Complete participant handover](SUBMISSION.md) | Research, demonstrations, starter, classifier evidence and explicit external dependencies |

GitHub Pages, instructor acceptance and actual teacher feedback remain pending.

Este repositório reúne os **exercícios, materiais de referência e desafios** de uma formação em inteligência artificial centrada na prática.

O percurso começa com **pesquisa, leitura crítica e produção de conhecimento** com IA. Depois avança para **engenharia de contexto, personalização de coding agents, desenvolvimento de software, testes e publicação** de uma aplicação real.

O ponto central não é aprender a copiar prompts ou obter respostas bonitas. É desenvolver a capacidade de **definir o problema, fornecer contexto, tomar decisões, delegar trabalho à IA e verificar se o resultado é verdadeiro**.

> [!IMPORTANT]
> **Não são fornecidos prompts prontos nem soluções completas dos exercícios.**
> Os participantes devem investigar, decidir e orientar os agentes. Há exemplos para análise e reutilização seletiva: **aproveitar o que funciona, adaptar o necessário e eliminar o que não serve. Não reinventar a roda — nem copiar sem compreender.**

## O percurso em dois dias

<table>
<tr>
<td width="50%" valign="top">

### 01 · Pesquisar com IA

**Microsoft Copilot no navegador**

Investigar a evolução dos modelos de linguagem, interagir com artigos científicos, cruzar evidências e produzir textos que resistam a uma revisão crítica.

**O participante aprende a:**

- Formular requisitos de pesquisa.
- Distinguir evidência, interpretação e hipótese.
- Analisar e cruzar documentos.
- Auditar e corrigir conteúdo gerado por IA.

**[Acessar o Dia 1 →](Dia1/README.md)**

</td>
<td width="50%" valign="top">

### 02 · Construir com agentes

**GitHub Copilot no VS Code · Modo agente**

Projetar um ambiente de trabalho reutilizável para agentes, desenvolver uma skill de bootstrap, planejar com GitHub Issues e construir uma aplicação de classificação de imagens.

**O participante aprende a:**

- Persistir contexto e procedimentos.
- Criar Agent Skills próprias.
- Delegar tarefas verificáveis em Issues e PRs.
- Treinar, testar, publicar e corrigir software.

**[Acessar o Dia 2 →](Dia2/README.md)**

</td>
</tr>
</table>

## Apresentações dos módulos (PDF)

Os slides da formação estão organizados por dia, na sequência dos módulos. Os arquivos foram otimizados para ter **menos de 20 MB cada**, mantendo todas as páginas. A apresentação conjunta GSS mantém o nome original do ficheiro.

### Dia 1 · Fundamentos de IA e LLMs

| Ordem | Apresentação |
| :---: | --- |
| 0 | [Whoami](Dia1/Teorico/Whoami.pdf) |
| 3 | [The Basics](Dia1/Teorico/The%20Basics.pdf) |
| 4 | [LLM Anatomy](Dia1/Teorico/LLM%20Anatomy.pdf) |
| 5 | [From LLM to Chatbot](Dia1/Teorico/From%20LLM%20to%20Chatbot.pdf) |
| 6 | [Context Eng](Dia1/Teorico/Context%20Eng.pdf) |
| 7 | [Model Chosing](Dia1/Teorico/Model%20Chosing.pdf) |

**[Apresentação conjunta GSS — Dia 1, módulos 1 e 2](Dia1/Teorico/20261012--forma%C3%A7%C3%A3o_gss_modulos_1.1_1.2-HCG-v_conjunta_dia1.pdf)**

### Dia 2 · Agentes e engenharia de software

| Ordem | Apresentação |
| :---: | --- |
| 2 | [Coding Agents](Dia2/Teorico/Coding%20Agents.pdf) |
| 3 | [Agentic Context Eng](Dia2/Teorico/Agentic%20Context%20Eng.pdf) |
| 4 | [Task eng](Dia2/Teorico/Task%20eng.pdf) |
| 5 | [VDD and Autonomy](Dia2/Teorico/VDD%20and%20Autonomy.pdf) |

> **Materiais já disponíveis:** os PDFs estão nas pastas [`Dia1/Teorico/`](Dia1/Teorico/) e [`Dia2/Teorico/`](Dia2/Teorico/).

## Demonstrações Python GSS — Dia 1

Os [12 exercícios dos módulos 1 e 2](Dia1/Exercicios-GSS/README.md) acrescentam
demonstrações de Machine Learning, redes neuronais e modelos de linguagem.
Estão numa pasta própria e usam nomes `dia1_modulo<N>_<ordem>_<nome>.py`.
O guia inclui a preparação do ambiente, os recursos e os testes.

## Dia 1 · Pesquisa, análise e pensamento crítico

O trabalho do primeiro dia é realizado com o **Microsoft Copilot na web**. Não exige VS Code nem programação. Cada exercício utiliza resultados da etapa anterior.

| Etapa | Exercício | O que será desenvolvido |
| :---: | --- | --- |
| **01** | [Pesquisa orientada](Dia1/Exercicio-01-Pesquisa-Orientada.md) | Investigar a evolução dos LLMs, de Transformers a arquiteturas modernas, e produzir um relatório fundamentado. |
| **02** | [Talk to a Paper](Dia1/Exercicio-02-Talk-to-a-Paper.md) | Analisar dois artigos científicos, identificar hipóteses, métodos, evidências e limitações. |
| **03** | [Cruzamento de fontes](Dia1/Exercicio-03-Cruzamento-de-Fontes.md) | Integrar relatórios e artigos num pequeno texto investigativo, distinguindo fatos de hipóteses sobre consciência e LLMs. |
| **04** | [Auditoria e refinamento](Dia1/Exercicio-04-Auditoria-e-Refinamento.md) | Revisar criticamente o texto com novas conversas, registrar correções e produzir uma versão mais consistente. |

**Resultado do Dia 1:** um conjunto de materiais de pesquisa, fichas de leitura, texto argumentativo e evidências de auditoria.

## Dia 2 · Engenharia de agentes e software real

No segundo dia, cada participante trabalha no **seu próprio repositório GitHub**, com o **GitHub Copilot no VS Code em modo agente**. O repositório evolui exercício após exercício: primeiro as regras de trabalho, depois o contexto específico do projeto e, por fim, a implementação.

| Etapa | Exercício | O que será desenvolvido |
| :---: | --- | --- |
| **01** | [Crie seu starter repository](Dia2/Exercicio-01-Starter-Repo.md) | Construir um ponto de partida reutilizável em que o agente conheça as suas regras, procedimentos e forma de trabalhar. |
| **02** | [Crie uma skill de bootstrap](Dia2/Exercicio-02-Skill-Bootstrap.md) | Projetar uma Agent Skill própria, inspirada na lógica **Ask Me**, que investigue requisitos e persista o contexto aprovado. |
| **03** | [Desenvolva o classificador](Dia2/Exercicio-03-Desenvolvimento-Issues.md) | Planejar em Issues, programar com o agente, treinar a rede neural, criar um site e verificar o resultado. |
| **04** | [Roda de feedback](Dia2/Exercicio-04-Roda-de-Feedback.md) | Submeter o app à avaliação do professor, discutir dúvidas e pendências e realizar correções verificáveis com o agente. |

### O desafio integrador

**Construir uma rede neural que reconheça dígitos manuscritos e apresentá-la em uma aplicação interativa publicada no GitHub Pages.**

O projeto utiliza o **MNIST** e culmina num site em que qualquer pessoa poderá:

- **Desenhar** um dígito com mouse, caneta ou toque.
- **Carregar imagens do computador**, individualmente ou em conjunto.
- Ver a **previsão e as pontuações** produzidas pelo modelo.
- Explorar uma **visualização baseada em informações reais da rede neural**.

Toda a inferência deverá acontecer **no navegador**, usando os pesos de uma rede **efetivamente treinada pelo participante**, sem API remota de classificação.

### Veja o produto final de referência

> [!TIP]
> **[Image-classifier-demo — abrir o repositório com a aplicação completa](https://github.com/vcanonici/Image-classifier-demo)**
>
> Projeto de referência desenvolvido por **Vinicius Canonici**: uma rede neural treinada com MNIST, integrada a uma interface interativa para desenhar dígitos, acompanhar previsões e visualizar pixels, ativações e conexões da rede. Os pesos são utilizados para **inferência diretamente no navegador**, sem backend.
>
> **A demonstração já permite desenho e upload de imagens.** Cabe aos participantes criar e verificar **sua própria rede e aplicação**, capaz de classificar os dez PNGs CAPTCHA do desafio. Analise, reutilize e adapte apenas componentes úteis, sem impor a arquitetura do exemplo.

<div align="center">

**60.000 imagens de treino** &nbsp;·&nbsp; **10.000 imagens de teste MNIST** &nbsp;·&nbsp; **10 imagens CAPTCHA no desafio final**

**[Acessar o MNIST](Dia2/Dataset-MNIST/README.md)** &nbsp;·&nbsp; **[Desafio oficial: 10 PNGs CAPTCHA](Dia2/Desafio/)** &nbsp;·&nbsp; **[Guia de avaliação](Dia2/Desafio/README.md)**

</div>

> [!CAUTION]
> O **único conjunto oficial do desafio** são os **dez PNGs CAPTCHA** em `Dia2/Desafio/`. Não devem ser utilizados para treino, validação ou escolha de hiperparâmetros. Registre as dez previsões antes de comparar com os rótulos, sem ajustar manualmente os resultados. Os dez arquivos estão diretamente nessa pasta, de `caso_01.png` a `caso_10.png`.

#### Exercício 3, em quatro partes

| Parte | Foco | Entregável |
| :---: | --- | --- |
| **3.1** | [Planejamento da rede neural](Dia2/Exercicio-03/Parte-01-Planejamento-da-Rede.md) | Especificação, decisões e **GitHub Issues criadas e aprovadas antes do código**. |
| **3.2** | [Coding com o agente](Dia2/Exercicio-03/Parte-02-Coding-com-o-Agente.md) | Rede implementada e treinada, testes, métricas e pesos exportáveis. |
| **3.3** | [Demonstração no GitHub Pages](Dia2/Exercicio-03/Parte-03-Site-GitHub-Pages.md) | Site interativo com desenho, **upload de imagens**, inferência local e visualização real da rede. |
| **3.4** | [Funciona com o test set?](Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md) | Dez previsões CAPTCHA documentadas, diagnóstico e avaliação honesta. |

O modelo de trabalho incentivado em todas as etapas é **Plan → Exec → Verify → Review → Commit**.

## Aprender com exemplos reais

Os materiais de referência não são respostas para entregar. São oportunidades para **investigar decisões de engenharia** e criar uma solução melhor ajustada ao próprio contexto.

| Referência | O que observar |
| --- | --- |
| **[Starter Repo de referência](Dia2/Referencia-Starter-Repo/LEIA-PRIMEIRO.md)** | Como um agente recebe regras persistentes, carrega procedimentos sob demanda, registra conhecimento e localiza skills, CLI tools e MCPs. |
| **[Arquivos do Starter Repo](Dia2/Referencia-Starter-Repo/Starter-Repo/)** | Examine a implementação, **reutilize e adapte** componentes úteis e **elimine** dependências e regras desnecessárias. |
| **[Guia de Agent Skills](Dia2/Guia-Skills-Copilot.md)** | Formato e descoberta de skills nativas do Copilot, fontes para pesquisa e criação manual **sem `npx`**. |
| **[Image-classifier-demo](https://github.com/vcanonici/Image-classifier-demo)** | Referência com desenho, **upload de imagens**, inferência local e visualização real da rede. A solução dos alunos deve ser própria. |
| **[Issue #1 — Exemplo didático](https://github.com/vcanonici/Formacao-de-IA/issues/1)** | Como especificar **contexto, objetivo, dependências, escopo, critérios de aceitação e evidências**. |
| **[PR #2 — Exemplo didático](https://github.com/vcanonici/Formacao-de-IA/pull/2)** | Como apresentar código, testes e CI para revisão. Usa um **classificador Python por centroides**, não uma rede neural; o PR é mantido aberto para estudo. |

### Como aproveitar os exemplos

**Analisar → Selecionar → Adaptar → Purgar → Verificar.**

Uma boa solução não é a que tem mais arquivos, dependências ou ferramentas: é a que dá ao agente **o contexto certo, as instruções certas e critérios claros para comprovar o trabalho**.

## Como utilizar este repositório

**Para participantes:** comece pelo [guia do Dia 1](Dia1/README.md) e siga os exercícios na ordem. No Dia 2, crie **um repositório seu** e utilize os arquivos desta formação como enunciados e referências. Não desenvolva o classificador dentro deste repositório da formação.

**Para docentes:** utilize os enunciados como guias para discussão e prática. O Dia 2 termina com uma **roda de feedback**, na qual cada aplicação é testada, as dúvidas são discutidas coletivamente e as correções são registradas em Issues e commits.

### Ambiente

| Dia 1 | Dia 2 |
| --- | --- |
| [Microsoft Copilot](https://copilot.microsoft.com/) no navegador | [VS Code](https://code.visualstudio.com/) e GitHub Copilot em modo agente |
| Navegador e acesso aos recursos permitidos pela conta | Conta GitHub, Git, terminal e possibilidade de publicar no GitHub Pages |
| Pesquisa e análise de documentos | Coding agent, versionamento, testes, treinamento e implantação |

As **Agent Skills em Markdown não exigem `npx` ou bibliotecas especiais para serem carregadas**. O projeto de machine learning poderá exigir dependências de desenvolvimento, a serem escolhidas e justificadas pelos participantes.

## Organização do repositório

```text
Formacao-de-IA/
├── Dia1/
│   ├── README.md                      # Percurso de pesquisa
│   ├── Exercicio-*.md                 # Quatro exercícios
│   ├── Exercicios-GSS/               # 12 demonstrações Python dos módulos 1 e 2
│   └── Teorico/                       # Sete apresentações em PDF
├── Dia2/
│   ├── README.md                      # Percurso com agentes
│   ├── Exercicio-01-Starter-Repo.md
│   ├── Exercicio-02-Skill-Bootstrap.md
│   ├── Exercicio-03-Desenvolvimento-Issues.md
│   ├── Exercicio-03/                  # Quatro partes do projeto
│   ├── Exercicio-04-Roda-de-Feedback.md
│   ├── Dataset-MNIST/                 # Dataset e verificação de integridade
│   ├── Desafio/                       # Dez PNGs CAPTCHA oficiais
│   ├── Referencia-Starter-Repo/       # Exemplo para análise seletiva
│   ├── Guia-Skills-Copilot.md
│   └── Teorico/                       # Quatro apresentações em PDF
├── LICENSE.md
└── CITATION.cff
```

## Autoria, licença e citação

Material de formação desenvolvido por **Vinicius Canonici e Hugo Gomes**.

Salvo indicação específica, os materiais didáticos deste repositório estão licenciados sob **[Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](LICENSE.md)**. Recursos de terceiros, datasets e repositórios externos mantêm suas próprias condições de uso e atribuição.

Se reutilizar os materiais, credite os autores e indique as alterações realizadas. Para referências bibliográficas, consulte o arquivo **[CITATION.cff](CITATION.cff)**.

---

<div align="center">

### Entender o problema. Orientar o agente. Verificar a evidência.

**A IA executa tarefas. Você define o que importa, como trabalhar e quando considerar o resultado válido.**

[↑ Voltar ao início](#formação-de-ia)

</div>
