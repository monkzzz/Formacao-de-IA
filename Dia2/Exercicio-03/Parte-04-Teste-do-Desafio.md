# Exercício 3 · Parte 4 — Funciona com o test set do desafio?

## Objetivo

Aprender a **avaliar uma aplicação de IA em condições reais**, diferenciando a qualidade medida no MNIST do comportamento obtido com imagens externas, e comprovando os resultados com evidências — não apenas com a afirmação do agente de que a solução funciona.

### Ponto de partida

A rede treinada e avaliada na Parte 2 e a **aplicação pública do GitHub Pages com upload de imagens** criada na Parte 3.

## Dois testes diferentes, duas conclusões diferentes

**Teste oficial do MNIST:** os 10.000 exemplos reservados servem para avaliar a generalização dentro desse conjunto de dados. Não devem ser usados para ajuste de hiperparâmetros.

**Desafio independente:** as [nove imagens disponibilizadas aqui](../Desafio/) têm características que podem diferir do MNIST. Elas servem para verificar se o **sistema completo**, incluindo upload, pré-processamento, inferência e interface, consegue classificá-las.

O objetivo do desafio é **9 acertos em 9 imagens**. Um resultado inferior deve ser registrado como tal, com diagnóstico. Acertar 9/9, isoladamente, **não comprova generalização**.

## Perguntas socráticas antes do teste

- Como comprovar que estamos avaliando os **pesos e a versão do site realmente publicados**?
- O teste deve começar **antes ou depois** de conhecer os rótulos das imagens? Por quê?
- Uma imagem pode ser interpretada de forma diferente se o navegador alterar seu tamanho, fundo, contraste ou orientação?
- Por que obter bons resultados no MNIST não garante o mesmo resultado nessas imagens?
- Como evitar que o agente use o nome `digito_*.png` ou o código gerador do desafio como se fossem a resposta da rede?
- Que evidência mostraria que a previsão veio do **conteúdo visual processado pelo modelo**, e não de uma regra especial?
- Se a imagem carregada produzir um resultado diferente do desenho manual equivalente, o que deve ser investigado?

## Procedimento de avaliação

1. **Fixar a versão:** registrar o commit, os pesos do modelo e a URL publicada **antes de observar e utilizar os rótulos para avaliar o desempenho**.
2. **Abrir o site público:** conferir que está usando a versão pretendida, sem servidor remoto de inferência.
3. **Carregar as nove imagens** do [diretório do desafio](../Desafio/) pela funcionalidade de upload. Pode ser uma a uma ou em conjunto.
4. **Registrar os resultados brutos**: identificador da imagem, previsão e escores que a aplicação apresentou. Guardar evidências de que a previsão veio da interface pública.
5. **Comparar com os rótulos** somente depois que as previsões estiverem registradas. Os arquivos possuem nomes que indicam o dígito; o algoritmo **não pode ler o nome para determinar a classe**. O script gerador também não pode ser usado como oráculo de inferência.
6. **Contabilizar os acertos e erros**, sem sobrescrever previsões nem ajustar manualmente os resultados após a comparação.
7. **Investigar as falhas** com o Copilot: o problema decorre do treinamento, do conjunto de dados, da preparação da imagem, da exportação, da inferência no navegador ou da interface?
8. **Documentar o resultado real** e a relação entre Issues, commits, testes e observações.

Se quiser aprimorar a solução depois de verificar os nove exemplos, registre essa nova iteração separadamente e **não a apresente como se fosse o teste independente original**.

## Matriz de verificação

Para cada ponto, registrar **PASS, FAIL, BLOCKED ou NOT RUN**, acompanhado de evidência:

| O que verificar | Evidência esperada |
| --- | --- |
| Rede treinada e avaliação MNIST | Código, pesos, logs, métricas e testes reais |
| Equivalência entre ambientes | Comparações documentadas das saídas sobre as mesmas entradas |
| Desenho no navegador | Previsão e pontuações exibidas a partir do modelo treinado |
| Upload de imagens | Seleção, pré-visualização e previsão para cada imagem |
| Inferência sem backend | Funcionamento client-side e ausência de chamada para classificação remota |
| GitHub Pages | URL pública funcional |
| Nove imagens do desafio | Nove previsões registradas antes de comparar com os rótulos |
| Rastreabilidade | Commit, Issues concluídas, resultados e limitações |

**Não declare aprovado o que não foi executado.**

## Entregável da parte 4

**Relatório de validação conciso** com URL pública, versão Git, versão dos pesos, métricas no MNIST, resultados das nove imagens, quantidade real de acertos, diagnóstico de falhas e evidências de que o upload e a inferência funcionaram no navegador.

**Próximo exercício:** apresentar ao professor o projeto, o repositório, o funcionamento da interface, as Issues e os aprendizados sobre a colaboração com o agente.
