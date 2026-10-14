# Dia 2 — Do starter repo à aplicação publicada

## Objetivo

Aprender a construir um ambiente para coding agents, criar **do zero uma skill de bootstrap baseada em perguntas**, transformar um desafio em **GitHub Issues** e desenvolver e apresentar uma solução com o **GitHub Copilot no VS Code (modo agente)**.

A IA deve ajudar a especificar, criar Issues, programar, treinar, testar, integrar e documentar. O aluno dirige o agente, decide e verifica. **Os exercícios não fornecem prompts prontos, skills implementadas, código de solução nem estimativas de tempo.**

**Ferramentas:** VS Code, GitHub Copilot em modo agente, Git, GitHub, terminal e GitHub Pages. Os recursos efetivamente disponíveis dependem das permissões da conta e do ambiente. Skills nativas escritas em Markdown **não exigem npx nem bibliotecas extras para serem carregadas**; o projeto de machine learning poderá ter outras dependências.

## Desafio integrador

O desafio oficial é classificar **[dez imagens de dígitos problemáticos em estilo CAPTCHA](Desafio/)**, contendo as classes **0–9** uma vez cada, usando **uma rede neural treinada pelos participantes com o Copilot**.

Criar também uma aplicação pública no **GitHub Pages**: qualquer pessoa deverá poder desenhar um número, receber a classificação e observar uma visualização com **informações reais da rede neural**. A inferência deverá acontecer **no próprio navegador**, sem API remota de classificação.

**Desafio oficial:** [dez PNGs CAPTCHA](Desafio/) e [guia de avaliação](Desafio/README.md). **Dataset obrigatório:** [MNIST](Dataset-MNIST/README.md), com 60.000 imagens de treino e 10.000 de teste, no formato IDX original.

Os dez PNGs CAPTCHA são reservados para a **verificação final**. Não podem ser usados para treinamento, validação, seleção de arquitetura ou ajuste de hiperparâmetros. O objetivo é investigar **quantos dos dez casos a rede classifica corretamente**, documentando previsões e causas dos erros; **10/10 não é condição para aprovação**. Os resultados do MNIST e do desafio são avaliações diferentes. Os dez arquivos estão diretamente em `Desafio/`, como `caso_01.png` a `caso_10.png`.

## Sequência obrigatória

1. [Exercício 1 — Construir seu próprio starter repo](Exercicio-01-Starter-Repo.md): a partir dos conceitos vistos em aula e da **análise crítica de um starter repo de referência**, reaproveitar o que funcionar, adaptar às próprias preferências e eliminar o que não for útil.
2. [Exercício 2 — Criar uma skill de bootstrap](Exercicio-02-Skill-Bootstrap.md): **compreender a lógica do padrão Ask Me e construir uma skill própria**, que entreviste o usuário e alimente o starter repo com o contexto do desafio.
3. [Exercício 3 — Rede neural, agente, site e desafio](Exercicio-03-Desenvolvimento-Issues.md): dividido em **quatro partes** — [planejamento da rede e criação de Issues](Exercicio-03/Parte-01-Planejamento-da-Rede.md), [coding com o agente](Exercicio-03/Parte-02-Coding-com-o-Agente.md), [site no GitHub Pages inspirado na demonstração, com upload de imagens](Exercicio-03/Parte-03-Site-GitHub-Pages.md) e [teste com dez imagens CAPTCHA](Exercicio-03/Parte-04-Teste-do-Desafio.md).
4. [Exercício 4 — Roda de feedback](Exercicio-04-Roda-de-Feedback.md): o professor testa os aplicativos, discute dúvidas com a turma, aponta pendências e orienta correções verificáveis com o agente.

## Apresentações teóricas

Estão disponíveis em [`Dia2/Teorico/`](Teorico/): [Coding Agents](Teorico/Coding%20Agents.pdf), [Agentic Context Eng](Teorico/Agentic%20Context%20Eng.pdf), [Task eng](Teorico/Task%20eng.pdf) e [VDD and Autonomy](Teorico/VDD%20and%20Autonomy.pdf).

**Material de referência disponível:** [Starter Repo para análise](Referencia-Starter-Repo/LEIA-PRIMEIRO.md) e [arquivos do exemplo](Referencia-Starter-Repo/Starter-Repo/). É permitido — e recomendado — **copiar, adaptar e reutilizar o que for útil**, sem recriar trabalho que já esteja bem resolvido. **Purgar documentos, procedimentos e dependências que não atendam às necessidades do aluno.** O material não é um repositório pronto para entrega: cada aluno deverá construir **o seu próprio starter repo**, com escolhas justificadas.

**Issue de referência para o Exercício 3:** [Issue #1 — Planejamento e especificação da rede MNIST](https://github.com/vcanonici/Formacao-de-IA/issues/1). Os participantes devem analisar os critérios de aceitação e **criar Issues próprias nos seus repositórios**; esta Issue é um exemplo, não uma tarefa a implementar no repositório da formação.

**PR de referência para o Exercício 3:** [PR #2 — Classificador simples em Python, com testes e CI](https://github.com/vcanonici/Formacao-de-IA/pull/2). Examine **Conversation**, **Files changed** e **Checks**: o exemplo ensina a submeter e revisar mudanças verificáveis. **Não é uma rede neural nem uma solução para copiar no projeto final; o PR permanece aberto, sem merge.**

**Material de apoio:** [Guia de criação de skills no VS Code e referências externas](Guia-Skills-Copilot.md).

## O que significa Ask Me?

É uma **estratégia de interação**, não uma skill já entregue: o agente identifica informações que faltam, faz perguntas relevantes, esclarece ambiguidades e registra decisões aprovadas **antes de começar a desenvolver**. No Exercício 2, cada aluno transforma essa lógica em uma skill de bootstrap capaz de popular **seu próprio starter repo**.

**Não há uma skill Ask Me incluída neste repositório.** Os catálogos externos são material para pesquisar, compreender o padrão e projetar uma solução própria.

## Entrega do Dia 2

Um **único repositório próprio** com starter, skill criada pelo aluno, contexto obtido no bootstrap, especificação, Issues, código, modelo treinado, avaliação, testes, site público, commits e evidências; além da avaliação coletiva e do registro de feedback e correções do Exercício 4.

**Referência pedagógica:** Engenharia de Agentes de IA — Cadernos 01 a 05.
