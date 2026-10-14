# Dia 2 — Prática integradora: do problema ao classificador publicado

## Objetivo

Aprender a trabalhar com **GitHub Copilot no Visual Studio Code como coding agent**: preparar o ambiente, construir contexto persistente, transformar um problema aberto em especificações, delegar tarefas de implementação, verificar resultados e publicar uma aplicação funcional.

Ao contrário do Dia 1, centrado no Microsoft Copilot no navegador para produção de relatórios, **o Dia 2 utiliza o GitHub Copilot no VS Code**, além de Git, GitHub, terminal, testes e GitHub Pages, conforme os recursos disponíveis no ambiente.

A IA deverá participar ativamente da investigação, do planejamento, da escrita do código, da execução dos testes e da documentação. Os participantes deverão **dirigir e supervisionar** esse trabalho, não programar toda a solução manualmente nem executar instruções que não compreendem.

**Referência pedagógica:** *Engenharia de Agentes de IA* — Cadernos 01 a 05.

## Desafio integrador

Um repositório disponibilizará **nove imagens de dígitos manuscritos**. O objetivo é desenvolver um sistema capaz de identificar os dígitos, treinando uma rede neural e disponibilizando uma aplicação web pública na qual qualquer pessoa possa desenhar um número, observar a classificação e inspecionar o comportamento real da rede.

A aplicação deverá executar a **inferência diretamente no navegador**, sem recorrer a uma API ou servidor remoto de classificação, e deverá ser publicada no **GitHub Pages**.

**Repositório das nove imagens:** endereço a ser fornecido pelo instrutor.

As nove imagens são um **desafio final**, não dados para treino ou ajuste. Os participantes deverão investigar fontes adicionais de dados e escolher justificadamente dataset, arquitetura, linguagem, framework, pré-processamento e formato de exportação do modelo.

## Como trabalhar

- Cada participante criará **seu próprio repositório GitHub** e desenvolverá a solução progressivamente. Não há starter repo nem arquitetura prontos para copiar.
- Os enunciados especificam **o que precisa ser alcançado**, mas não fornecem prompts, código, comandos de instalação nem decisões técnicas resolvidas. Cabe ao participante conversar com o agente e orientar sua execução.
- Cada exercício parte dos artefatos produzidos nos anteriores. O repositório deverá evoluir conforme a especificação e os testes justificarem novas necessidades.
- Mudanças relevantes exigem aprovação humana. Um resultado descrito pelo agente não substitui evidências reais, como saídas de testes, diffs, métricas ou a aplicação publicada.
- Trabalhar por pequenas unidades verificáveis, seguindo o ciclo **Plan → Exec → Verify → Review → Commit**. Documentar falhas e limitações sem declará-las resolvidas.

## Sequência de exercícios

1. [Exercício 1 — Bootstrap do starter repository](Exercicio-01-Bootstrap-do-Repositorio.md)
2. [Exercício 2 — Investigação e especificação](Exercicio-02-Investigacao-e-Especificacao.md)
3. [Exercício 3 — Implementação, treinamento e avaliação](Exercicio-03-Implementacao-e-Treinamento.md)
4. [Exercício 4 — Delegação do desenvolvimento do site](Exercicio-04-Desenvolvimento-do-Site.md)
5. [Exercício 5 — Inferência no navegador e publicação](Exercicio-05-Inferencia-e-Publicacao.md)
6. [Exercício 6 — Auditoria e desafio das nove imagens](Exercicio-06-Validacao-Final.md)
7. [Exercício 7 — Retrospectiva dos coding agents](Exercicio-07-Retrospectiva.md)

## Entrega integradora

Ao concluir, apresentar **um repositório próprio** com especificação, Issues, código, testes, processo reproduzível de treinamento, pesos, avaliação, aplicação web, histórico de mudanças e documentação; **uma URL pública** no GitHub Pages; e evidências do desafio das nove imagens.

> O objetivo não é descobrir um prompt mágico nem copiar uma solução. É aprender a construir um contexto operacional no qual um agente possa executar tarefas reais, com decisões humanas e resultados verificáveis.
