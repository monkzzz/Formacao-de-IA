# Dia 2 — Do starter repo à aplicação publicada

## Objetivo

Aprender a construir um ambiente para coding agents, criar uma **skill de bootstrap baseada em perguntas**, transformar um desafio de programação em **GitHub Issues** e desenvolver e apresentar uma solução com o **GitHub Copilot no VS Code (modo agente)**.

A IA deve ajudar a fazer o trabalho de engenharia: especificar, criar Issues, programar, treinar, testar, integrar e documentar. O aluno é responsável por orientar o agente, decidir, supervisionar e verificar. **Não há prompts prontos, código de solução nem tempos estipulados.**

**Ferramentas:** VS Code, GitHub Copilot em modo agente, Git, GitHub, terminal e GitHub Pages. Recursos dependem das permissões da conta e do ambiente. As **skills em Markdown não exigem npx**, mas as dependências que vierem a ser escolhidas para treinar o modelo são outra questão.

## Desafio integrador

Um repositório do professor disponibiliza **nove imagens de dígitos manuscritos**. Construir, com auxílio do agente, um sistema que identifique os dígitos por meio de **uma rede neural treinada no projeto**.

A solução deverá incluir uma aplicação pública no **GitHub Pages**, em que qualquer pessoa desenhe um número, receba a classificação e observe uma visualização baseada em **informações reais da rede neural**. A inferência deverá executar no **próprio navegador**, sem API remota de classificação.

**Link das nove imagens:** a ser informado pelo professor.

As nove imagens são reservadas para a **verificação final**. Não são um dataset de treinamento e não devem ser utilizadas no treino nem na escolha de hiperparâmetros. Os alunos investigarão dados adequados, arquitetura, métricas, framework e métodos de exportação; nenhuma solução específica está prescrita. O objetivo do desafio é **9 acertos em 9 imagens**, relatando o resultado real, sem correções manuais. Isso não substitui métricas em um conjunto de teste independente.

## Sequência obrigatória

1. [Exercício 1 — Construir o starter repo](Exercicio-01-Starter-Repo.md). Criar uma estrutura genérica para trabalho com agentes.
2. [Exercício 2 — Criar e testar a skill de bootstrap](Exercicio-02-Skill-Bootstrap.md). Desenvolver uma skill própria, baseada no conceito Ask Me, para entrevistar o usuário e popular o starter repo com contexto do desafio.
3. [Exercício 3 — Planejar em Issues e desenvolver](Exercicio-03-Desenvolvimento-Issues.md). **Primeiro** fazer o agente propor e criar as Issues do projeto inteiro, revisar e aprovar; **depois** implementar por Issue.
4. [Exercício 4 — Apresentação final](Exercicio-04-Apresentacao.md). Demonstrar o produto, os resultados e a colaboração com o agente.

**Material de apoio:** [Guia de skills nativas para VS Code e catálogos públicos](Guia-Skills-Copilot.md).

## Skill de referência incluída

Este repositório contém uma skill didática Ask Me em [`.github/skills/ask-me/SKILL.md`](../.github/skills/ask-me/SKILL.md). Ela permite experimentar a técnica de entrevista **sem npx, Node.js ou pacotes adicionais**. Trata-se de uma referência genérica; no Exercício 2 o aluno criará **sua própria skill de bootstrap**, não apenas copiará a referência.

## Entrega do Dia 2

Um **único repositório próprio** evoluído durante os exercícios, com starter, skill criada pelo aluno, contexto, especificação, Issues, código, modelo treinado, resultados, testes, site público, commits e evidências; além de demonstração ao professor.

**Referência pedagógica:** Engenharia de Agentes de IA — Cadernos 01 a 05.
