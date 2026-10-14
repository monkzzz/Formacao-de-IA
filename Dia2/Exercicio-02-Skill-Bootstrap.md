# Exercício 2 — Skill de bootstrap no estilo Ask Me

## Objetivo

Aprender a **criar uma Agent Skill nativa do GitHub Copilot no VS Code**, que faça perguntas antes de configurar o projeto e utilize as respostas para **popular o starter repo do Exercício 1 com contexto persistente**.

O participante desenvolverá sua **própria skill de bootstrap** com auxílio do coding agent. O objetivo não é instalar uma solução pronta nem copiar a skill de referência.

## Pesquisa e exploração inicial

Estudar o princípio **Ask Me**: antes de implementar, o agente identifica o que ainda não sabe e entrevista a pessoa, com perguntas adaptativas, para estabelecer requisitos, restrições, decisões e pontos que precisam de validação.

Explorar a skill genérica disponibilizada no repositório, em `../.github/skills/ask-me/SKILL.md`, e pesquisar outras skills de entrevista e inicialização nos [catálogos indicados no guia](Guia-Skills-Copilot.md).

Observar a diferença entre uma **skill de perguntas genéricas** e uma **skill de bootstrap**, cujo resultado é persistido na estrutura do projeto.

## Ficha de requisitos

Usar o Copilot para projetar uma skill que:

- Identifique o estado atual da seed e leia o contexto já existente.
- Faça **perguntas progressivas e pertinentes**, sem repetir informações que já conhece.
- Investigue objetivo, restrições, requisitos, dados, validação, ferramentas e publicação, conforme as lacunas que surgirem.
- Distinga **decisões confirmadas, hipóteses e pendências**, sem inventar respostas do usuário.
- Discuta alternativas relevantes com o participante sem escolher tudo silenciosamente.
- Apresente uma síntese da entrevista e **solicite aprovação antes de modificar arquivos**.
- Após a aprovação, **atualize o starter repo com contexto de projeto**, documentação, decisões, próximos passos e orientações ao agente.
- Preserve regras genéricas úteis, evite sobrescrever decisões válidas e permita repetir ou retomar o processo.
- Seja utilizável **como skill local do VS Code**, sem instaladores, `npx`, scripts obrigatórios ou bibliotecas adicionais.

## Construção no VS Code

A partir do [guia de skills](Guia-Skills-Copilot.md), criar a pasta e o arquivo `SKILL.md` com nome, descrição e instruções apropriadas. **Os alunos devem definir o comportamento real da sua skill**; não há implementação pronta do bootstrap no enunciado.

Distinguir o local de descoberta nativa da skill, como `.github/skills/<nome>/SKILL.md`, de um eventual catálogo interno `AgentDATA/skills/`. Um índice de skills não garante que o Copilot vá carregá-las.

## Experimento

1. Testar se o Copilot consegue descobrir a nova skill e **realmente entrevistá-los antes de criar arquivos**.
2. Aplicar a skill ao desafio das nove imagens apresentado no README do Dia 2.
3. Responder às perguntas, corrigir pressupostos e aprovar o contexto produzido.
4. Deixar o agente registrar esse contexto **no mesmo repositório** construído no Exercício 1.
5. Testar nova conversa: o agente deverá recuperar o objetivo e as decisões **sem depender do histórico da entrevista**.
6. Refinar a skill se ela fizer perguntas inúteis, presumir informações ou omitir contexto importante.

A skill deve preparar o projeto para o planejamento do Exercício 3; **não precisa implementar o classificador nem definir antecipadamente arquitetura ou dataset**.

## Entregável

**Skill própria, em SKILL.md, testada e versionada**, e **starter repo populado com contexto do projeto** resultante da entrevista.
