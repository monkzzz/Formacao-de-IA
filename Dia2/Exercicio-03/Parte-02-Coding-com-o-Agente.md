# Exercício 3 · Parte 2 — Coding com o agente

## Objetivo

Aprender a **delegar e supervisionar o trabalho de programação ao GitHub Copilot no VS Code**, desenvolvendo, treinando e avaliando uma rede neural com o **[MNIST](../Dataset-MNIST/README.md)**.

### Ponto de partida

O starter repo contextualizado, a especificação e as **GitHub Issues aprovadas na Parte 1**.

Nesta parte o **Copilot executa o trabalho técnico**: escreve código, prepara dados, treina, testa e investiga erros. Você decide, autoriza e verifica — não é necessário escrever manualmente toda a implementação.

## Desenvolva por Issues, não com um único pedido genérico

Para cada tarefa, utilize o método de trabalho definido no seu starter repo, praticando o ciclo **Plan → Exec → Verify → Review → Commit**:

1. O agente lê o contexto, a Issue, os arquivos relevantes e o estado Git.
2. Propõe um plano curto com os arquivos afetados, as verificações previstas e os riscos.
3. Implementa a tarefa **aprovada**, utilizando suas ferramentas e o ambiente disponível.
4. Executa testes, treinamento ou experimentos **reais**, apresenta resultados e corrige falhas observadas.
5. Você revisa o diff, os resultados e as limitações antes de aceitar ou pedir ajustes.
6. Registra a evolução em commits ou Pull Requests relacionados às Issues.

### Perguntas socráticas durante a implementação

**Dados**

- Como o agente comprova que carregou o MNIST corretamente, com imagens e rótulos correspondentes?
- Que verificações mostram as dimensões, classes e transformações dos dados?
- Como impedir vazamento entre treino, validação e teste?

**Modelo**

- Os arquivos implementados correspondem à arquitetura aprovada?
- Como um teste pode identificar erro nas dimensões de entrada e saída antes de iniciar o treino?
- A solução foi dividida em responsabilidades claras ou o agente concentrou tudo num código difícil de verificar?

**Treinamento**

- Como você saberá que o modelo foi **realmente treinado**, em vez de utilizar um resultado simulado ou pesos de terceiros?
- Que parâmetros, versões e sementes devem ser documentados para repetir o experimento?
- Como interpretar a evolução de perda e desempenho? O que fazer se o resultado for inadequado?

**Testes e avaliação**

- Como comprovar a qualidade em exemplos que não participaram do treino?
- O que uma **matriz de confusão** pode mostrar que a acurácia sozinha não mostra?
- As métricas vieram da execução real? Onde estão os logs e resultados?
- Por que não utilizar o conjunto de teste oficial para escolher hiperparâmetros?

**Preparação para o site**

- Os pesos, o pré-processamento e a descrição da arquitetura podem ser exportados de forma que o navegador consiga executá-los?
- Que testes serão necessários para verificar a equivalência entre a inferência de origem e a versão web?

## Verificações obrigatórias

O repositório deverá conter evidências de:

- Código e processo reproduzível para carregar dados, treinar e avaliar.
- Modelo treinado, **pesos gerados no projeto** e informações necessárias à inferência.
- Métricas reais em dados reservados, análise de erros e, quando aplicável, curvas de treino.
- Testes de comportamento e dimensões, além de validação de exportação do modelo.
- Issues atualizadas, diffs revisados, commits e documentação.

**Não utilize as nove imagens do desafio para ajuste do modelo.** Elas serão processadas na Parte 4, pela interface do site.

## Entregável da parte 2

**Rede neural treinada e avaliada**, com pesos exportáveis, testes, métricas e processo documentado, pronta para integração na aplicação web.

**Ponto de verificação:** o agente deve demonstrar, por comandos e arquivos existentes, que consegue repetir a avaliação e obter previsões reais com o modelo que treinou.
