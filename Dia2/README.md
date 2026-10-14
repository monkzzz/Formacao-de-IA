# Dia 2 — Do starter repo à aplicação publicada

## Objetivo

Aprender a construir um ambiente para coding agents, criar **do zero uma skill de bootstrap baseada em perguntas**, transformar um desafio em **GitHub Issues** e desenvolver e apresentar uma solução com o **GitHub Copilot no VS Code (modo agente)**.

A IA deve ajudar a especificar, criar Issues, programar, treinar, testar, integrar e documentar. O aluno dirige o agente, decide e verifica. **Os exercícios não fornecem prompts prontos, skills implementadas, código de solução nem estimativas de tempo.**

**Ferramentas:** VS Code, GitHub Copilot em modo agente, Git, GitHub, terminal e GitHub Pages. Os recursos efetivamente disponíveis dependem das permissões da conta e do ambiente. Skills nativas escritas em Markdown **não exigem npx nem bibliotecas extras para serem carregadas**; o projeto de machine learning poderá ter outras dependências.

## Desafio integrador

O professor disponibilizará **nove imagens de dígitos manuscritos**. Desenvolver, com auxílio do agente, um sistema que as classifique usando **uma rede neural treinada pelos participantes com o Copilot**.

Criar também uma aplicação pública no **GitHub Pages**: qualquer pessoa deverá poder desenhar um número, receber a classificação e observar uma visualização com **informações reais da rede neural**. A inferência deverá acontecer **no próprio navegador**, sem API remota de classificação.

**Link das nove imagens:** a ser informado pelo professor.

As nove imagens são reservadas para a **verificação final**: não servem para treinamento nem ajuste de hiperparâmetros. Dataset, arquitetura, framework, métricas e exportação serão investigados e decididos pelos alunos. O objetivo do desafio é **9 acertos em 9 imagens**, com resultados reais e sem correções manuais; isso não substitui avaliação em conjunto de teste independente.

## Sequência obrigatória

1. [Exercício 1 — Construir seu próprio starter repo](Exercicio-01-Starter-Repo.md): a partir dos **conceitos vistos em aula**, projetar e construir **do zero** uma estrutura genérica para trabalho com agentes, sem template fornecido.
2. [Exercício 2 — Criar uma skill de bootstrap](Exercicio-02-Skill-Bootstrap.md): **compreender a lógica do padrão Ask Me e construir uma skill própria**, que entreviste o usuário e alimente o starter repo com o contexto do desafio.
3. [Exercício 3 — Planejar em Issues e desenvolver](Exercicio-03-Desenvolvimento-Issues.md): **primeiro** fazer o agente planejar o projeto completo por Issues e aprová-las; **depois** implementar e verificar cada etapa.
4. [Exercício 4 — Apresentação final](Exercicio-04-Apresentacao.md): demonstrar ao professor o produto funcionando e as evidências do trabalho com o agente.

**Não existe starter repo disponibilizado pela formação.** O repositório desta formação contém apenas os enunciados e o material conceitual; o starter será criado no GitHub de cada aluno.

**Material de apoio:** [Guia de criação de skills no VS Code e referências externas](Guia-Skills-Copilot.md).

## O que significa Ask Me?

É uma **estratégia de interação**, não uma skill já entregue: o agente identifica informações que faltam, faz perguntas relevantes, esclarece ambiguidades e registra decisões aprovadas **antes de começar a desenvolver**. No Exercício 2, cada aluno transforma essa lógica em uma skill de bootstrap capaz de popular **seu próprio starter repo**.

**Não há uma skill Ask Me incluída neste repositório.** Os catálogos externos são material para pesquisar, compreender o padrão e projetar uma solução própria.

## Entrega do Dia 2

Um **único repositório próprio** com starter, skill criada pelo aluno, contexto obtido no bootstrap, especificação, Issues, código, modelo treinado, avaliação, testes, site público, commits e evidências; além da apresentação ao professor.

**Referência pedagógica:** Engenharia de Agentes de IA — Cadernos 01 a 05.
