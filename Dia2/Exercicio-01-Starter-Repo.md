# Exercício 1 — Construção de um starter repository

## Objetivo

Aprender a usar o GitHub Copilot no VS Code para criar um **starter repo genérico e reutilizável** para projetos desenvolvidos com coding agents. **Não iniciar ainda o classificador de dígitos.**

## Referência

O professor apresentou um exemplo de starter repo baseado em um contrato de atuação no arquivo `AGENTS.md` e uma área `AgentDATA/` destinada a contexto, procedimentos, conhecimento, ferramentas e registros.

Essa estrutura é uma **referência de organização**, não uma árvore obrigatória para reproduzir automaticamente. Os participantes deverão entender o propósito dos componentes e decidir com o agente quais são realmente necessários.

## Ficha de requisitos

- Criar um repositório GitHub próprio e abri-lo no VS Code com o GitHub Copilot em modo agente.
- Fazer o agente **inspecionar o repositório e as ferramentas disponíveis antes de alterar arquivos**.
- Discutir que informações um agente precisa para começar uma tarefa, localizar documentos, compreender limites e validar mudanças.
- Construir uma seed com um **contrato operacional claro**, um README e locais definidos para contexto persistente, procedimentos, habilidades e registros, conforme a organização adotada.
- Considerar a separação entre **instruções gerais** e procedimentos especializados, que devem ser consultados quando forem relevantes.
- Definir um procedimento básico de trabalho e critérios para aprovar alterações, executar testes, registrar decisões e realizar commits.
- Evitar segredos versionados e não declarar disponíveis ferramentas, skills ou integrações que ainda não foram verificadas.
- Criar um commit que identifique a versão inicial da seed.

## Verificação

Iniciar **uma nova conversa** com o agente e avaliar se ele compreende a função da seed, identifica suas regras, sabe onde buscar contexto e reconhece o que ainda não está definido.

## Entregável

**Starter repo funcional como estrutura genérica**, versionado no GitHub. O repositório ainda não deverá conter arquitetura de rede, código de treinamento, dataset ou interface do classificador.

No exercício seguinte, a seed receberá contexto específico por meio de uma skill criada pelos alunos.
