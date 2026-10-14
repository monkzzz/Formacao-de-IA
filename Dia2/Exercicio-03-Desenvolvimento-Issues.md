# Exercício 3 — Do desafio ao classificador: planejar por Issues, desenvolver e publicar

## O desafio

Você já criou **seu próprio starter repository** (Exercício 1) e utilizou sua **skill de bootstrap baseada em perguntas** para incorporar o contexto de um projeto (Exercício 2).

Agora chegou a hora de colocar esse ambiente à prova: **oriente o GitHub Copilot no VS Code, em modo agente, para construir um sistema que reconheça dígitos manuscritos**.

O projeto deverá conter uma **rede neural realmente treinada**, uma avaliação documentada e uma **aplicação pública no GitHub Pages**. Qualquer pessoa deverá conseguir desenhar um dígito, pedir a classificação e observar informações **reais** sobre o comportamento da rede.

A inferência deverá acontecer **dentro do navegador**, sem servidor de classificação. O modelo deve ser aquele efetivamente treinado no projeto.

**Antes de implementar o código, o agente deverá planejar o projeto inteiro e criar as GitHub Issues necessárias.** Os alunos deverão revisar essas Issues e supervisionar sua execução.

> Este exercício descreve problemas, requisitos e perguntas para investigação. **Não fornece prompts, arquitetura da rede, framework, código de treinamento ou implementação do site.** O Copilot fará o trabalho de engenharia sob sua orientação.

## Os dados disponibilizados

Use o **[MNIST](Dataset-MNIST/README.md)**, disponibilizado no repositório por arquivos compactados e por um procedimento reproduzível de obtenção. É uma base de dígitos manuscritos com **60.000 imagens de treino e 10.000 imagens de teste**, em **escala de cinza, com 28 × 28 pixels**, abrangendo classes **0 a 9**.

Também existem **[nove imagens do desafio](Desafio/)**, que deverão ser classificadas **somente na verificação final**, depois de fixar a versão do modelo. Não utilize essas nove imagens para treinar, escolher hiperparâmetros, selecionar a arquitetura ou corrigir manualmente os resultados.

O uso do **MNIST é obrigatório**. A arquitetura, a linguagem, as ferramentas, o método de treinamento e o mecanismo de inferência no browser serão escolhas investigadas pelos participantes.

## Parte 1 — Compreender o problema antes de criar Issues

### 1.1. O que significa reconhecer um número?

- Qual é exatamente a entrada do sistema? O que esperamos receber como saída?
- Uma imagem representando um dígito é a mesma coisa que o número representado por ele?
- O que significa uma rede neural estar **treinada** para essa tarefa?
- Como distinguir uma previsão real de uma resposta pré-programada ou uma interface que apenas parece funcionar?
- Quais decisões técnicas o agente pode propor, e quais precisam ser aprovadas por você?

**Com o agente:** esclareça o desafio e registre os requisitos e critérios de sucesso no contexto do projeto.

### 1.2. O que o MNIST resolve — e o que não resolve?

- Como os arquivos do MNIST representam **pixels e rótulos**?
- Qual a diferença entre os exemplos usados para aprender e os exemplos reservados para avaliar?
- Por que seria problemático escolher hiperparâmetros observando constantemente o desempenho no conjunto de teste?
- Como investigar o formato, a distribuição das classes e possíveis inconsistências **antes de treinar**?
- Se uma rede tiver excelente resultado no MNIST, isso garante que funcionará com qualquer desenho produzido no site?
- As **nove imagens do desafio** possuem as mesmas características visuais das imagens do MNIST? O que pode mudar?

**Com o agente:** inspecione os dados e proponha uma estratégia de pré-processamento, treino, validação e teste. O conjunto de teste do MNIST não deve ser usado para orientar o ajuste do modelo.

### 1.3. Que rede neural construir?

- Quais alternativas de rede neural fazem sentido para classificar imagens pequenas?
- Quais são as vantagens, limitações e custos de treinamento dessas alternativas no computador disponível?
- Como decidir dimensões de entrada, camadas, neurônios, ativações e formato da saída?
- O que um número de desempenho isolado **não** revela sobre erros e generalização?
- Quais escolhas devem ficar documentadas para permitir repetir o experimento?
- Se a rede não aprender ou apresentar resultados ruins, como o agente poderá investigar as causas com evidências?

**Com o agente:** discutir alternativas e registrar decisões, **sem receber uma arquitetura prescrita pelo enunciado**.

### 1.4. Como o modelo chegará ao navegador?

- Onde acontecerá o treinamento? Onde acontecerá a inferência no produto final?
- Como transformar os pesos aprendidos em um formato utilizável numa página estática?
- O desenho feito com mouse ou toque terá as mesmas dimensões, cores, proporções e orientação das imagens usadas no treino?
- Que transformações precisam ser equivalentes entre treinamento e interface?
- Como conferir que a versão no navegador produz resultados compatíveis com o modelo original?
- Como comprovar que não existe uma chamada escondida para uma API de classificação?

**Com o agente:** antecipar restrições da integração web ainda na especificação.

### 1.5. O que o usuário deveria conseguir observar?

- Como permitir que uma pessoa desenhe, apague e desenhe novamente?
- O sistema deveria mostrar somente a classe escolhida ou também outras informações?
- Qual a diferença entre uma pontuação do modelo e uma probabilidade calibrada?
- O que seria uma visualização **honesta** da rede: arquitetura, ativações, saídas intermediárias ou outra representação fundamentada?
- Como reconhecer se uma animação da interface é apenas decorativa?
- O que é necessário para que o site funcione corretamente no GitHub Pages?

**Com o agente:** definir uma experiência web verificável, sem escrever a implementação nesta fase.

## Parte 2 — Transformar o projeto em GitHub Issues

Agora use seu starter repo contextualizado para orientar o Copilot a **decompor toda a solução antes de programar**.

### Perguntas socráticas sobre a decomposição

- Se uma Issue disser apenas “criar uma rede neural”, como saber se está suficientemente definida?
- Qual é a menor unidade de trabalho cujo resultado pode ser **verificado de forma objetiva**?
- O agente consegue identificar **dependências** entre tarefas antes de executá-las?
- Por que um projeto que treina corretamente no computador ainda pode falhar no browser?
- Quem define os critérios de aceitação: o agente ou o responsável pelo projeto?
- Que evidências deverão acompanhar cada Issue para que o participante confie na sua conclusão?
- O que deve acontecer quando a implementação revelar uma hipótese errada ou exigir mudança de requisitos?

### Áreas que o planejamento precisa abranger

As Issues, produzidas pelo agente e aprovadas pelo participante, deverão cobrir o ciclo completo:

- **Preparação e verificação do MNIST**, inclusive a separação adequada dos dados e a rastreabilidade de sua origem.
- **Investigação e design da rede neural**, com alternativas e decisões documentadas.
- **Implementação e treinamento**, com processo reproduzível e pesos realmente produzidos.
- **Testes e avaliação**, com métricas em dados reservados, análise de erros e matriz de confusão.
- **Exportação e integração do modelo** para inferência client-side.
- **Site interativo** para desenhar e classificar dígitos e inspecionar o comportamento real da rede.
- **Publicação no GitHub Pages** e testes na URL pública.
- **Validação independente das nove imagens** e relatório de resultados.

**Não há uma quantidade de Issues predefinida.** Cabe ao participante avaliar se o plano do agente é completo, se a granularidade faz sentido e se cada Issue possui objetivo, dependências, critérios de aceitação e forma de comprovação.

**Regra obrigatória:** criar e revisar as Issues **antes de iniciar a implementação**. Se o agente não tiver permissão para criá-las no GitHub, deverá orientar um procedimento compatível com os recursos disponíveis, a ser autorizado pelo participante. Um plano escrito apenas no chat não substitui as Issues no repositório.

## Parte 3 — Construir com o agente, uma Issue de cada vez

Com o plano aprovado, conduza o Copilot em um ciclo **Plan → Exec → Verify → Review → Commit**.

Para cada Issue:

1. **Contexto:** o agente lê a Issue, as instruções do starter repo, as decisões relevantes e o estado do Git.
2. **Plano:** identifica arquivos e comportamento afetados, riscos e verificações previstas.
3. **Execução:** implementa **a tarefa delimitada**, utilizando ferramentas reais.
4. **Verificação:** roda testes, treinamento, build ou experimentos pertinentes, e apresenta as saídas observadas.
5. **Revisão:** o participante inspeciona alterações, resultados e possíveis limitações.
6. **Registro:** documenta o que mudou e cria commits ou PRs rastreáveis.

O **Copilot deve escrever código, executar treinamento e ajudar a depurar**. Não se espera que o aluno implemente manualmente a solução inteira. Seu trabalho é decidir, orientar e verificar.

### Perguntas para fazer a si mesmo durante a execução

- O agente concluiu a tarefa **ou apenas afirmou que a concluiu**?
- Quais testes e comandos realmente executou? Quais ainda faltam?
- As métricas foram calculadas a partir do modelo treinado ou são números ilustrativos?
- A mudança respeitou as decisões já documentadas?
- O agente alterou arquivos fora da Issue? Por quê?
- O que precisa ser acrescentado ao contexto persistente para melhorar a próxima tarefa?

## Parte 4 — Verificação do produto e desafio final

Não confunda **o modelo ter aprendido MNIST** com **o site estar integrado e funcional**.

Antes da entrega, comprove que:

- O treinamento pode ser reproduzido e os pesos têm origem verificável.
- A avaliação utiliza exemplos reservados, sem vazamento para treino ou escolha de hiperparâmetros.
- Existe análise de erros e resultados reais, não apenas uma afirmação de “alta acurácia”.
- A aplicação carrega os pesos do projeto e classifica desenhos no próprio navegador.
- O pré-processamento da interface é coerente com o usado no treinamento.
- A visualização da rede se baseia em informações reais, não em animações arbitrárias.
- A aplicação funciona em uma **URL pública do GitHub Pages**.
- GitHub Issues, commits e documentação permitem rastrear o trabalho.

### As nove imagens do desafio

- Fixar e registrar a versão do modelo **antes** de utilizar os rótulos das nove imagens.
- Executar as nove classificações e registrar as previsões produzidas.
- Comparar previsões e rótulos **sem alterar manualmente nenhuma saída**.
- Apontar acertos, erros e possíveis causas.
- O objetivo do desafio é **9/9**. Se o resultado for inferior, registrar o resultado real e o diagnóstico: **não declarar 9/9 sem evidências**.

**Atenção:** as imagens do desafio disponibilizadas neste repositório possuem nomes de arquivo que indicam os dígitos. **Não usar esses nomes, nem o script que as gerou, para guiar o treino ou as previsões.** A avaliação deve utilizar somente os pixels como entrada do modelo. Um conjunto de teste adicional e independente continua necessário para avaliar generalização.

## Entregável

**Um repositório GitHub próprio**, desenvolvido com o agente a partir das Issues, contendo especificação, código, pipeline de treino e teste, pesos, resultados, documentação, histórico Git e site público funcional.

A apresentação final, no Exercício 4, deverá demonstrar **o funcionamento real da solução e as evidências**, além do processo de colaboração com o coding agent.
