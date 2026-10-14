# Exercício 3 — Planejamento por Issues e execução do projeto

## Objetivo

Aprender a orientar o coding agent para **decompor o desafio completo em GitHub Issues**, aprovar um plano verificável e **desenvolver a solução de programação por etapas**, utilizando o contexto criado pela skill no Exercício 2.

## Desafio

Construir e treinar uma **rede neural de classificação de dígitos manuscritos** e publicar uma interface interativa no **GitHub Pages**. A inferência ocorrerá **no navegador**, usando os pesos reais treinados no projeto.

O professor fornecerá nove imagens para o desafio final. Elas não poderão ser usadas no treinamento nem no ajuste do modelo.

## Parte A — Criar todas as Issues antes de implementar

Fazer o agente ler os requisitos e decisões persistidos no repositório e, a partir deles, **investigar e organizar a implementação completa em Issues**. O planejamento deverá contemplar, no mínimo:

- **Projeto da rede:** levantamento de alternativas, arquitetura, entradas, saídas e escolhas justificadas.
- **Dados e treinamento:** fontes e licenças dos dados, preparação, divisão dos conjuntos, processo de treinamento e geração dos pesos.
- **Testes da rede:** verificações funcionais, conjunto de teste não utilizado no treino ou ajuste, métricas e análise de erros.
- **Integração web:** exportação do modelo, compatibilidade de pré-processamento e inferência dentro do navegador.
- **Site:** área para desenhar com mouse ou toque, repetir a tentativa, apresentar a previsão e inspecionar informação **real** da rede, não apenas elementos decorativos.
- **Publicação:** implantação estática no GitHub Pages e validação da URL pública.
- **Desafio final:** avaliação das nove imagens reservadas e documentação de resultados.

Não existe um número obrigatório de Issues. O agente deverá criar **quantas forem necessárias** para que cada tarefa tenha dependências, critérios de aceitação e evidências verificáveis.

**Revisar e aprovar as Issues antes de começar o código.** Se a integração do GitHub não permitir criá-las automaticamente, usar os recursos autorizados do VS Code, GitHub CLI ou interface web para concretizar o plano no repositório.

## Parte B — Desenvolver uma Issue de cada vez

Para cada Issue, usar o ciclo **Plan → Exec → Verify → Review → Commit**:

1. O agente consulta contexto, instruções, Issue e estado do Git.
2. Apresenta um plano curto com arquivos previstos e testes.
3. Implementa a tarefa autorizada.
4. Executa os comandos, testes ou experimentos reais que forem pertinentes.
5. Apresenta diff, saídas, métricas e problemas encontrados.
6. O participante revisa, aprova a alteração e registra um commit ou PR relacionado à Issue.

O agente deverá **escrever código, treinar, testar e corrigir o software**. O papel do aluno é direcionar, decidir e verificar, não implementar tudo manualmente.

## Verificação do produto

Conferir, por evidências:

- Fonte, separação e pré-processamento dos dados de treino, validação e teste.
- Rede treinada, pesos produzidos, métricas reais, matriz de confusão e análise de erros.
- Consistência das inferências do modelo original e da versão executada no navegador.
- Interface que realmente usa o modelo treinado e permite desenhar, limpar e classificar.
- Visualização baseada em características ou saídas reais da rede.
- Site publicado e testado em uma URL pública do GitHub Pages, sem servidor remoto de inferência.
- Issues, commits e documentação correspondentes ao trabalho concluído.

**Desafio das nove imagens:** fixar a versão do modelo antes de revelar os rótulos, registrar nove previsões e compará-las aos valores de referência. O objetivo é **9/9**, mas falhas precisam ser reportadas sem manipular resultados. Isso não equivale à avaliação de generalização no conjunto de teste.

## Entregável

**Projeto implementado a partir de Issues**, incluindo rede treinada, testes, métricas, pesos, aplicação pública, histórico Git e evidências suficientes para demonstrar ao professor o que realmente funcionou.
