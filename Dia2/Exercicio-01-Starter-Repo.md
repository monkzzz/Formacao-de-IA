# Exercício 1 — Criar o próprio starter repository

## Objetivo

Com base **nos conceitos de starter repository e de engenharia de contexto estudados em aula**, cada participante deverá **projetar e construir do zero o seu próprio starter repo**, utilizando o **GitHub Copilot no VS Code (modo agente)**.

**Não será fornecido um starter repo, um template, uma estrutura de pastas para reproduzir nem um repositório-modelo.** O desafio é transformar o que foi aprendido em aula em uma estrutura funcional, com o auxílio do agente.

O starter repo deverá ser **genérico e reutilizável**: um ambiente preparado para receber diferentes projetos de desenvolvimento com IA. **Ainda não é para desenvolver o classificador de dígitos.**

## O problema que o starter repo deve resolver

Imagine que um coding agent começa a trabalhar em um repositório novo. Como ele descobrirá:

- Qual é a finalidade do repositório e que regras de trabalho deve seguir?
- Onde encontrar o contexto de um projeto e como saber se uma informação está atualizada?
- Como localizar procedimentos, habilidades e ferramentas relevantes, sem carregar tudo indiscriminadamente?
- O que pode executar por conta própria e quais ações precisam de aprovação humana?
- Como planejar alterações, testar resultados, registrar decisões e manter o histórico?
- Como continuar um projeto em outra sessão, sem depender da conversa anterior?

O participante deverá usar essas perguntas para **conceber o funcionamento do próprio starter repo**, não apenas criar diretórios.

## Ficha de requisitos

### 1. Projetar a organização

- Criar **um repositório GitHub próprio e inicialmente vazio** e abri-lo no VS Code.
- Discutir com o Copilot que responsabilidades um starter repo deve assumir.
- Decidir **quais arquivos e diretórios criar, como nomeá-los e por que eles são necessários**.
- Evitar gerar automaticamente uma solução inteira sem compreender e aprovar a organização proposta.

### 2. Preparar o agente para trabalhar

- Definir instruções persistentes que expliquem o propósito do repositório, as regras de atuação, como localizar contexto e como executar e validar tarefas.
- Decidir como separar orientações gerais de procedimentos consultados apenas quando forem necessários.
- Estabelecer limites de autonomia e as situações em que o agente deverá consultar o participante.

### 3. Organizar contexto e recursos reutilizáveis

O starter repo deverá prever uma forma compreensível de organizar:

- **Contexto de projetos:** objetivos, requisitos, restrições e decisões.
- **Conhecimento e documentação:** referências e informações relevantes para outras sessões.
- **Procedimentos:** métodos reutilizáveis para realizar e verificar tarefas.
- **Skills:** como registrar, localizar e utilizar capacidades especializadas.
- **Ferramentas e integrações:** inventário de recursos, incluindo CLI e MCP, diferenciando o que está realmente disponível do que é apenas uma possibilidade.
- **Registros:** decisões, modificações, resultados e problemas que mereçam persistir.

**A escolha da estrutura é do aluno.** Essas categorias são necessidades a resolver, não nomes obrigatórios de pastas.

### 4. Tornar o starter repo utilizável

- Pedir ao Copilot que **crie efetivamente** a estrutura aprovada, com documentação e instruções coerentes entre si.
- Definir pelo menos um procedimento genérico útil para o trabalho com agentes, incluindo uma maneira de conferir resultados.
- Criar documentação para que outra pessoa ou sessão do agente compreenda como utilizar e evoluir o starter repo.
- Evitar arquivos sem finalidade, comandos que não foram verificados e segredos versionados.
- Versionar o resultado com Git e realizar um commit identificável.

## Verificação

Após a construção, **iniciar uma nova conversa** com o Copilot no VS Code e verificar se ele consegue, consultando somente o repositório:

1. Explicar para que serve o starter repo e como está organizado.
2. Localizar as instruções e o contexto necessários para começar uma tarefa.
3. Identificar onde guardar informações e decisões de um projeto futuro.
4. Reconhecer suas regras de atuação e como validar alterações.

Se não conseguir, **refinar a estrutura com o agente** e repetir a verificação.

## Entregável

**Um starter repository original, criado pelos próprios participantes com o GitHub Copilot e publicado em seu GitHub**, com organização justificada, instruções persistentes, mecanismos para contexto e recursos, procedimentos reutilizáveis, documentação e histórico de commits.

**Critério central:** demonstrar que a estrutura realmente ajuda um agente a iniciar e continuar trabalho em projetos distintos.

**Próximo exercício:** os participantes criarão sua **própria skill de bootstrap baseada na lógica Ask Me**, capaz de entrevistar o usuário e **popular o starter repo que acabaram de construir** com o contexto do projeto de classificação de dígitos.
