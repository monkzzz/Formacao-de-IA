# Exercício 2 — Investigação do problema e especificação colaborativa

## Objetivo da atividade

Aprender a transformar um problema ainda aberto em **requisitos, decisões técnicas, critérios de aceitação e tarefas delegáveis**, por meio de conversas com o GitHub Copilot.

**Conceitos:** Caderno 03 — seleção de contexto e registro de decisões; Caderno 04 — Task Engineering, Spec-Driven Development (SDD) e planejamento.

## Material de partida

O starter repository do Exercício 1 e as **nove imagens de dígitos manuscritos** disponibilizadas pelo instrutor. O objetivo final continua sendo o classificador treinado e a aplicação publicada no GitHub Pages.

**As nove imagens não são um dataset de treinamento.** Não devem ser usadas para treinar, selecionar hiperparâmetros ou adaptar o modelo aos casos do desafio.

## Ficha de investigação

Utilizar o Copilot para investigar e discutir os seguintes pontos **antes de solicitar a implementação completa**:

1. **Compreender as imagens:** examinar formatos, características visuais e implicações para a entrada do classificador. Distinguir observações verificáveis de hipóteses.
2. **Investigar estratégias de classificação:** comparar abordagens possíveis e discutir que tipo de rede neural pode resolver o problema nas condições previstas.
3. **Planejar os dados:** pesquisar fontes adicionais de dígitos manuscritos, verificar origem e licença, e decidir aquisição, pré-processamento, divisão entre treino, validação e teste.
4. **Especificar o modelo:** discutir com o agente dimensão e representação da entrada, camadas, neurônios, função de perda e outros elementos relevantes; registrar alternativas e justificativas.
5. **Planejar o treinamento e a avaliação:** definir métricas, critérios mínimos de qualidade, experimentos reproduzíveis e cuidados contra vazamento de dados.
6. **Considerar o site desde o início:** estudar como exportar o modelo e realizar inferência local no navegador, mantendo o pré-processamento compatível entre treinamento e aplicação.
7. **Formalizar os requisitos:** produzir uma especificação com funções esperadas, restrições, critérios de aceitação, evidências necessárias, dúvidas e decisões pendentes.
8. **Decompor o projeto:** criar GitHub Issues pequenas e verificáveis, com dependências, prioridades e critérios claros.

## Regras da atividade

- O **participante define e aprova** os critérios de sucesso; o agente pode propor alternativas e questionar pressupostos.
- Não iniciar a implementação completa antes de aprovar uma especificação suficientemente clara.
- Não existe arquitetura, dataset, quantidade de neurônios, framework ou linguagem obrigatória. Essas escolhas devem resultar da investigação.
- Separar **avaliação em dados de teste representativos** da **verificação final nas nove imagens**. Acertar nove exemplos isolados não demonstra generalização.
- Registar no repositório as decisões importantes, inclusive aquelas que foram abandonadas.

## Ponto de verificação

Selecionar uma Issue criada e verificar se uma nova conversa com o agente consegue entender **o que executar, quais arquivos consultar e como saber que a tarefa foi concluída**, sem precisar reconstruir todas as decisões oralmente.

## Entregável

**Especificação técnica revisada**, estratégia de aquisição e tratamento dos dados, critérios de aceitação e **GitHub Issues** organizadas para orientar a implementação.
