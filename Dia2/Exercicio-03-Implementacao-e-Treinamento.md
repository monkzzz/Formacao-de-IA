# Exercício 3 — Implementação, treinamento e avaliação do classificador

## Objetivo da atividade

Aprender a **delegar implementação e experimentação a um coding agent**, trabalhando em unidades pequenas, supervisionando modificações e verificando resultados com evidências reais.

**Conceitos:** Caderno 02 — ciclo de ação e observação; Caderno 04 — decomposição de tarefas; Caderno 05 — Verification-Driven Development (VDD).

## Material de partida

Starter repository, especificação aprovada e Issues do Exercício 2. A solução deverá seguir **as decisões técnicas tomadas pelos participantes**, sem impor uma arquitetura pronta.

## Atividades

Trabalhar com o Copilot a partir de Issues ou outras unidades pequenas, cobrindo os seguintes blocos:

1. **Dados:** implementar aquisição e carregamento da fonte selecionada, pré-processamento e divisão em treino, validação e teste. Verificar classes, formatos, dimensões e possíveis inconsistências.
2. **Modelo:** implementar a rede neural especificada e verificar entradas, saídas, dimensões e comportamento esperado. Qualquer mudança de arquitetura deverá ser justificada e registrada.
3. **Treinamento:** construir e executar o processo de treino. Registrar configurações, hiperparâmetros, versões, sementes aleatórias quando aplicável, resultados e artefatos produzidos.
4. **Avaliação:** medir desempenho com dados reservados, analisar erros e gerar **matriz de confusão**. O conjunto de teste não deverá ser usado para escolher hiperparâmetros.
5. **Visualização e documentação:** produzir curvas de perda e desempenho, exemplos de acertos e erros e, quando fizer sentido, representações internas da rede. Documentar o que os resultados mostram e o que não mostram.

## Ciclo de trabalho obrigatório

Em **cada tarefa ou Issue**, praticar o ciclo **Plan → Exec → Verify → Review → Commit**:

1. Fazer o agente consultar a Issue, a especificação, as regras do repositório e o estado do Git.
2. Analisar um plano breve com arquivos afetados, verificações previstas e possíveis riscos.
3. Autorizar a execução de uma unidade delimitada de trabalho.
4. Pedir ao agente que execute ferramentas, testes e comandos reais, interprete as falhas e corrija o que for necessário.
5. Examinar o **diff**, as saídas de testes, as métricas e as limitações declaradas.
6. Aceitar ou rejeitar a alteração e criar um commit identificável quando estiver validada.

**Não usar um pedido único para implementar o projeto inteiro.** A divisão em etapas e o controle sobre o agente fazem parte do exercício.

## Cuidados de avaliação

- Os **nove exemplos do desafio final** permanecem fora do treinamento e do ajuste do modelo.
- Não apresentar resultados inventados como se fossem logs ou métricas executadas.
- Se um teste não for executado, registrar esse fato; não tratá-lo como aprovado.
- Alterações de requisitos precisam ser refletidas na especificação ou nas Issues, em vez de incorporadas silenciosamente.

## Entregável

**Modelo treinado**, código e procedimento de treinamento reproduzíveis, pesos/artefatos, resultados de teste, matriz de confusão, visualizações, documentação, Issues atualizadas e commits rastreáveis.
