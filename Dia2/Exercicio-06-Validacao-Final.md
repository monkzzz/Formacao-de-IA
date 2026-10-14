# Exercício 6 — Auditoria final e desafio das nove imagens

## Objetivo da atividade

Aprender a **verificar uma solução desenvolvida com coding agents usando resultados observáveis**, aplicar critérios de aceitação e investigar falhas sem manipular o resultado final.

**Conceitos:** Caderno 05 — oráculos, Definition of Done, testes, integração contínua, revisão e evidências.

## Material de partida

Repositório próprio, modelo treinado, avaliação em dados reservados e aplicação pública dos exercícios anteriores; **nove imagens de dígitos manuscritos** fornecidas pelo instrutor, cujos rótulos servem para a verificação final.

## Desafio

O objetivo é classificar corretamente **as nove imagens (9/9)** usando a **versão final do modelo fixada antes de conhecer os rótulos do desafio**.

Essas imagens **não poderão ter sido usadas** no treinamento, seleção de hiperparâmetros ou adaptação do modelo. Um resultado inferior a 9/9 não poderá ser apresentado como cumprimento desse objetivo; os erros deverão ser descritos e diagnosticados.

O desafio das nove imagens é **independente** das métricas de generalização obtidas em um conjunto de teste representativo.

## Procedimento

1. Identificar e registrar qual versão de código, configuração e pesos será avaliada, **antes de revelar os rótulos** das imagens.
2. Pedir ao agente que processe as nove imagens usando o mesmo fluxo de entrada e classificação previsto para a aplicação.
3. Registrar para cada imagem o identificador, a classe prevista e, quando disponível, a confiança ou os escores produzidos.
4. Comparar as previsões com os rótulos de referência fornecidos pelo instrutor.
5. Apontar acertos, erros e possíveis causas: dados, treinamento, pré-processamento ou integração.
6. Auditar os demais critérios do projeto a partir de evidências reais, não de afirmações do agente.

## Matriz mínima de aceitação

| ID | Critério | Evidência esperada |
| --- | --- | --- |
| CA-01 | Starter repo criado pelo participante | Git, README, instruções, procedure e skill |
| CA-02 | Contexto recuperável em nova sessão | Agente identifica objetivo, regras, comandos e estado do projeto |
| CA-03 | Especificação construída e aprovada | Requisitos, decisões, alternativas e Issues |
| CA-04 | Dados obtidos e preparados | Origem, licença, transformações e divisão dos dados |
| CA-05 | Rede implementada e treinada | Código, configurações, pesos e logs reais |
| CA-06 | Avaliação em dados não vistos | Métricas, curvas, matriz de confusão e análise de erros |
| CA-07 | Site desenvolvido a partir de Issue | Issue, diff, testes e commits ou PR |
| CA-08 | Inferência executada no navegador | Demonstração client-side, sem API de classificação |
| CA-09 | Site publicado | URL pública funcional no GitHub Pages |
| CA-10 | Nove imagens classificadas | Nove previsões registradas e comparadas aos rótulos |
| CA-11 | Processo auditável | Histórico Git, decisões, testes e limitações |

Para **cada critério**, registrar **PASS, FAIL, BLOCKED ou NOT RUN**, com a evidência correspondente. Testes não executados não podem ser classificados como aprovados.

## Entregável

**Relatório curto de verificação**, matriz de aceitação preenchida, previsões das nove imagens, diagnóstico dos erros, URL pública, identificação da versão Git e evidências dos testes realizados.
