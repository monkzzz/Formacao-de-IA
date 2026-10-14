# Exercício 3 · Parte 1 — Planejamento da rede neural

## Objetivo

Aprender a utilizar o GitHub Copilot como **agente de investigação e planejamento**, transformando o desafio de reconhecer dígitos manuscritos em decisões técnicas verificáveis e **GitHub Issues para a solução inteira**.

### Ponto de partida

O repositório que você criou, já contextualizado com a sua skill de bootstrap, e o [MNIST disponibilizado nesta formação](../Dataset-MNIST/README.md).

Nesta parte você **não deve pedir a implementação integral**. O objetivo é sair de um problema aberto com uma especificação aprovada e um plano executável por Issues.

## Investigue o problema com perguntas socráticas

### Dados e requisitos

- O que a rede receberá como entrada e o que deverá devolver como resultado?
- Como os arquivos do MNIST armazenam pixels e rótulos?
- Qual a diferença entre **treinar**, **validar** e **testar** uma rede?
- Como utilizar o conjunto de teste do MNIST sem deixá-lo influenciar a escolha da arquitetura ou dos hiperparâmetros?
- Como um desenho criado no navegador pode diferir das imagens usadas no treino?
- Por que as [nove imagens do desafio](../Desafio/) precisam ficar fora da preparação do modelo?

### Arquitetura e treinamento

- Que arquiteturas de rede neural poderiam reconhecer imagens pequenas de dígitos?
- Como comparar alternativas quanto a qualidade, simplicidade, custo de treinamento e compatibilidade com o navegador?
- Quem definirá dimensões de entrada, camadas, neurônios, funções de ativação e formato da saída?
- Como saber se o modelo está aprendendo, se está sobreajustado ou se deixou de melhorar?
- Que métricas e resultados de testes permitiriam sustentar uma conclusão sobre seu desempenho?
- Como registrar dados, configuração, pesos, versões e decisões para reproduzir o treinamento?

### Integração com a aplicação

- Como exportar os **pesos realmente treinados** para que funcionem em um site estático?
- Como reproduzir no navegador o mesmo pré-processamento de imagens usado no treino?
- Como verificar a consistência entre a previsão calculada no ambiente de treinamento e no navegador?
- Que funcionalidades mínimas o site precisará para desenhar, **carregar imagens**, classificar e apresentar uma visualização real da rede?

**Sua tarefa:** discutir essas questões com o agente, investigar alternativas e **registrar os requisitos, as decisões aprovadas, os pressupostos e as dúvidas pendentes**. Não existe uma arquitetura obrigatória a reproduzir.

> **Veja como uma Issue deve ser escrita:** [Issue #1 — Especificar a rede neural MNIST e a estratégia de validação](https://github.com/vcanonici/Formacao-de-IA/issues/1). É um **exemplo didático** publicado no repositório da formação: contém contexto, dependências, limites, entregáveis, critérios de aceitação e evidências. **Não é para resolver essa Issue aqui.** Examine a estrutura, reaproveite o que for útil e crie as Issues **no seu próprio projeto**, ajustadas às suas decisões. Não copie automaticamente a arquitetura de outro projeto.

## Transforme todo o projeto em GitHub Issues

Antes de pedir ao Copilot que programe, faça-o organizar **todas as fases do trabalho** em Issues reais no GitHub do seu projeto: preparação do MNIST, design da rede, treinamento, testes e avaliação, exportação, aplicação web, upload de imagens, visualização da rede, publicação e validação final.

Pergunte a si mesmo:

- Uma Issue como “fazer o modelo” permitiria verificar sua conclusão? Como torná-la menor e mais objetiva?
- Qual tarefa depende da anterior? O que pode ser feito independentemente?
- Que artefato ou evidência demonstrará que uma Issue foi resolvida?
- As Issues cobrem também **o upload e a classificação das imagens do desafio**, e não apenas o desenho manual?
- Que decisões requerem aprovação humana antes de serem implementadas?

**Não há número fixo de Issues.** O importante é que cada uma tenha escopo, dependências, critérios de aceitação e verificações. Revisar com o agente a sequência proposta, aprovar as Issues e confirmar que elas existem de fato no GitHub. Se o agente não puder escrevê-las diretamente, utilizar um meio autorizado para publicá-las.

## Entregável da parte 1

**Especificação técnica e conjunto de GitHub Issues aprovadas**, organizadas para desenvolver o modelo, a aplicação e o teste final.

**Ponto de verificação:** numa nova conversa, o agente deve conseguir identificar a próxima Issue, compreender suas dependências e explicar como verificará o resultado **consultando o repositório**, sem depender do histórico anterior.
