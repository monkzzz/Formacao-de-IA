# Exercício 1 — Bootstrap do starter repository

## Objetivo da atividade

Aprender a **preparar um repositório para colaborar com um coding agent**. O starter repository não será fornecido: cada participante deverá construí-lo com o GitHub Copilot no VS Code, descobrindo quais informações, instruções e ferramentas o agente necessita.

**Conceitos:** Caderno 01 — objetivos, ferramentas, autonomia e critérios de parada; Caderno 02 — coding agents e harness; Caderno 03 — contexto operacional do repositório.

## Ponto de partida

Criar um **repositório GitHub próprio e vazio**, abri-lo no VS Code e verificar a disponibilidade do GitHub Copilot em modo agente no ambiente utilizado.

Neste exercício ainda **não é necessário construir ou treinar o classificador**. A tarefa é organizar as condições para desenvolvê-lo nos exercícios seguintes.

## Ficha de requisitos

A partir do desafio apresentado no [README do Dia 2](README.md), utilizar o Copilot para:

1. **Investigar o estado inicial do repositório** antes de pedir que crie arquivos. O que existe? Que ferramentas e comandos estão disponíveis?
2. **Realizar o bootstrap por perguntas:** fazer com que o agente identifique informações em falta e pergunte sobre objetivo, restrições, funcionamento, verificação e publicação.
3. **Escolher a stack inicial**, discutindo alternativas, dependências e comandos de instalação, execução e teste; justificar o que foi escolhido e o que ainda permanece em aberto.
4. **Criar a estrutura mínima útil** do repositório para começar a trabalhar, sem copiar indiscriminadamente um template ou antecipar toda a solução.
5. **Produzir um README** que explique a finalidade do projeto, os requisitos do ambiente e como iniciar e validar o trabalho.
6. **Definir instruções persistentes para o agente**, usando, quando compatível com o ambiente, o arquivo .github/copilot-instructions.md. Avaliar se AGENTS.md acrescenta orientação útil, evitando instruções contraditórias.
7. **Criar pelo menos uma procedure de trabalho** (por exemplo, o processo de validar alterações) e **uma skill reutilizável**, documentando quando utilizá-la e conferindo se a instalação do Copilot realmente a reconhece. Caso haja incompatibilidades, registrá-las e investigar uma alternativa.
8. **Definir limites de autonomia:** que arquivos o agente pode alterar, que comandos deve executar ou verificar e que operações exigem autorização humana?
9. **Versionar as decisões** com Git e criar um commit identificável.

## Como realizar

Conduzir a criação **por diálogo com o agente**. Observar se ele faz perguntas relevantes, diferencia o que sabe do que está assumindo, e justifica os arquivos que propõe criar. Não aceitar alterações desnecessárias só porque foram sugeridas.

Verificar com o Copilot os comandos reais de inicialização e teste, em vez de considerar a documentação suficiente por si só.

## Ponto de verificação

**Encerrar a conversa com o agente e iniciar outra sessão.** Verificar se o Copilot consegue recuperar, apenas pelo conteúdo do repositório, o objetivo, a estrutura, os comandos, as regras de atuação e o próximo passo. Identificar o contexto perdido e corrigir a documentação quando necessário.

## Entregável

**Starter repository próprio**, com README, instruções persistentes, procedure, skill reutilizável ou limitação comprovada de compatibilidade, comandos verificáveis e primeiro commit. O repositório deve permitir a continuidade do projeto em outra sessão.
