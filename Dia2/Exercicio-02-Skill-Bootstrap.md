# Exercício 2 — Criar uma skill de bootstrap inspirada no conceito Ask Me

## Objetivo da atividade

Aprender **como funciona uma skill baseada em entrevista** e utilizar o GitHub Copilot no VS Code para **conceber, criar e testar uma skill própria**. A skill deverá coletar o contexto necessário para um novo projeto e, com aprovação do participante, **popular o starter repo criado no Exercício 1**.

**Ninguém receberá a implementação da skill pronta.** O exercício consiste em entender seu comportamento desejado, transformar essa compreensão em instruções para o coding agent e avaliar se a skill construída realmente funciona.

## Entendendo a ideia por trás de Ask Me

O padrão **Ask Me** inverte uma situação comum: em vez de o agente começar a criar arquivos ou escrever código a partir de um pedido incompleto, ele **investiga o que ainda precisa saber**.

O que importa compreender:

- **Descoberta de lacunas:** quais informações o pedido e o repositório já fornecem? O que falta para tomar decisões confiáveis?
- **Entrevista progressiva:** perguntas pertinentes surgem conforme as respostas anteriores, em vez de um formulário fixo que presume todos os problemas possíveis.
- **Esclarecimento:** respostas vagas, inconsistentes ou contraditórias exigem aprofundamento, não adivinhação.
- **Decisões versus hipóteses:** o que o usuário confirmou é diferente do que o agente supôs ou sugeriu.
- **Critério de parada:** quando já existe contexto suficiente para preparar o projeto, a entrevista deve poder terminar; pontos não resolvidos podem permanecer documentados.
- **Aprovação humana:** compreender o projeto não significa autorização automática para alterá-lo.
- **Persistência:** as respostas e decisões precisam sobreviver à conversa, tornando-se documentação reutilizável pelo agente.

Uma **skill Ask Me genérica** pode terminar com uma entrevista e sua síntese. A **skill de bootstrap** deste exercício deve ir além: depois de validar as informações, ela precisará transformá-las em **contexto organizado dentro do starter repo**, respeitando a estrutura que o aluno criou.

## Pesquisa antes de construir

Pesquisar exemplos de skills de entrevista em diretórios públicos e compreender seus princípios de funcionamento. Consultar [catálogos e documentação](Guia-Skills-Copilot.md), incluindo referências do padrão Ask Me.

Ao pesquisar, analisar criticamente:

- Que situação deveria ativar a skill?
- Como ela identifica informações que ainda não foram respondidas?
- Como evita perguntas irrelevantes ou repetidas?
- Como diferencia investigação, planejamento e autorização de execução?
- Que artefatos devem resultar da entrevista, e onde eles devem ser guardados?
- Como detectar se o agente **efetivamente usou** a skill?

**Não copiar nem instalar uma skill externa como solução do exercício.** Os exemplos servem para compreender a lógica e comparar possibilidades.

## Ficha de requisitos da skill a ser criada

Utilizando o Copilot, cada participante deverá projetar uma skill própria que:

1. Reconheça o contexto já existente no starter repo, sem presumir que o projeto foi definido.
2. Entreviste o usuário sobre os pontos relevantes ainda em aberto: objetivos, escopo, requisitos, restrições, dados, ferramentas, avaliação e publicação.
3. Formule **perguntas adaptativas** e trate ambiguidades sem inventar respostas.
4. Distinga **informação confirmada, hipótese e decisão pendente**.
5. Organize uma proposta de contexto do projeto e solicite validação do participante **antes de escrever ou alterar os arquivos**.
6. Após a aprovação, **popule a estrutura de contexto do próprio starter repo**, respeitando suas convenções, preservando regras genéricas e decisões anteriores.
7. Permita retomar ou atualizar o contexto futuramente, sem recomeçar a entrevista do zero.
8. Funcione como **Agent Skill nativa do GitHub Copilot no VS Code**, baseada em Markdown, **sem npx, instaladores ou bibliotecas especiais para a skill**.

Os participantes deverão decidir **como instruir o agente para atingir cada requisito**. Não é fornecido o conteúdo de um `SKILL.md` pronto ou um roteiro de perguntas para copiar.

## Como criar e testar com o Copilot

O [guia de skills](Guia-Skills-Copilot.md) explica o **formato técnico mínimo** e como o VS Code identifica uma skill: por exemplo, um arquivo `.github/skills/<nome-da-skill>/SKILL.md` com metadados e instruções escritas pelo participante.

A atividade consiste em:

1. Investigar o funcionamento de Agent Skills no ambiente e decidir como a skill de bootstrap deverá atuar.
2. Orientar o Copilot na criação **da skill do próprio aluno**, dentro de seu repositório.
3. Testar se o agente realmente a reconhece e **faz perguntas antes de propor alterações**.
4. Aplicar a skill ao **desafio do classificador de dígitos** descrito no README do Dia 2.
5. Responder à entrevista e verificar como as informações são organizadas, corrigidas e validadas.
6. Autorizar o agente a **popular o starter repo com contexto específico** do projeto.
7. Abrir uma **nova conversa** e verificar se o agente recupera os requisitos, as decisões e as pendências sem depender do histórico anterior.
8. Refinar a skill quando ela perguntar mal, presumir decisões, modificar arquivos precocemente ou registrar contexto insuficiente.

**Não implementar o classificador, criar as Issues do projeto nem escolher uma arquitetura como resposta predefinida nesta etapa.** A skill prepara o contexto que será usado no Exercício 3.

## Entregável

**Skill de bootstrap desenvolvida pelo aluno e versionada**, acompanhada do **starter repo populado com o contexto do projeto**, evidências de teste da skill e confirmação de que esse contexto é recuperável em nova sessão.
