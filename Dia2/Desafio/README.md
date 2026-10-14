# Desafio oficial — 10 dígitos CAPTCHA

O **único conjunto oficial do desafio do Dia 2** está na pasta:

## [Abrir os dez PNGs CAPTCHA](Avancado/)

São os arquivos **`caso_01.png` a `caso_10.png`**, uma imagem de cada dígito de **0 a 9**, contendo linhas cruzadas, fragmentos, traços partidos, deformações e oclusões. Eles foram criados para testar uma rede treinada no MNIST em situações visualmente difíceis.

Os participantes deverão classificá-los pela **rede neural que treinarem**, na própria aplicação GitHub Pages, usando a funcionalidade de **upload de imagens**.

- **[Conheça os arquivos e suas características](Avancado/README.md)**
- **[Exercício 3 · Parte 4 — avaliação dos dez dígitos](../Exercicio-03/Parte-04-Teste-do-Desafio.md)**

**Regras:** não utilizar essas dez imagens para treino, validação ou escolha de hiperparâmetros; registrar as dez previsões brutas antes de verificar os rótulos; relatar erros sem alterar os resultados. O teste do MNIST e o desempenho neste desafio medem aspectos diferentes.

## Arquivos históricos

Ainda estão presentes diretamente em `Dia2/Desafio/` os arquivos antigos `digito_1.png` a `digito_9.png`. **Eles não fazem parte do desafio oficial e não são necessários para a entrega dos alunos.** Use exclusivamente `Avancado/caso_01.png` a `Avancado/caso_10.png`.

O gerador dos casos CAPTCHA está disponível para auditoria, mas os participantes não devem utilizá-lo para consultar os rótulos antes de registrar as previsões.
