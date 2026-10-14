# Exercício 3 · Parte 4 — A rede funciona com os dez dígitos CAPTCHA?

## Objetivo

Avaliar **o sistema inteiro**, e não apenas a acurácia no MNIST: carregar imagens visualmente difíceis na aplicação pública, registrar as previsões reais e compreender os erros de inferência, pré-processamento e integração.

## Qual é o test set oficial?

O conjunto oficial é composto **exclusivamente pelos dez arquivos `caso_01.png` a `caso_10.png`** em **[Dia2/Desafio/](../Desafio/)**, com uma imagem de cada dígito **0 a 9**. Eles contêm linhas cruzadas, traços partidos, fragmentos, deformações, oclusões e ruído ao estilo CAPTCHA. Não são exemplos do MNIST.

**Há duas avaliações diferentes:**

- **Teste MNIST:** 10.000 exemplos reservados, não utilizados para escolher hiperparâmetros. Mede a generalização dentro do conjunto MNIST.
- **Desafio CAPTCHA:** dez imagens externas ao MNIST que testam também o upload, a preparação dos pixels, a inferência no navegador e a robustez da rede.

O objetivo é registrar **quantos dos dez casos** o modelo realmente acerta. **10/10 é desejável, mas não obrigatório.** Uma previsão incorreta ou um caso ambíguo deve ser relatado sem manipular resultados.

## Perguntas socráticas

- Por que uma rede eficaz em dígitos limpos pode errar quando linhas cruzam um algarismo?
- O que acontece com recorte, normalização e centro de massa quando há fragmentos de tinta fora do dígito?
- Como diferenciar um erro causado pelo modelo de um erro causado pelo pré-processamento no navegador?
- Como comprovar que as previsões vêm dos pixels e dos **pesos realmente treinados**, não de regras fixas?
- Por que retreinar após conhecer o resultado dessas dez imagens invalida uma segunda tentativa como avaliação independente?
- E quando a própria imagem é ambígua até para uma pessoa?

## Procedimento

1. **Fixar a versão antes do teste:** registrar commit, identificação dos pesos e URL pública do GitHub Pages. Não escolher arquitetura, modelo ou hiperparâmetros com base nas dez imagens.
2. **Abrir o app publicado:** verificar que a inferência acontece no navegador, sem API remota de classificação.
3. **Carregar os dez PNGs** de [Dia2/Desafio/](../Desafio/) pelo recurso de upload; individualmente ou em seleção múltipla.
4. **Registrar dez previsões brutas:** identificador do arquivo, classe prevista, pontuações e evidências da interface **antes de consultar qualquer rótulo**.
5. **Comparar com o gabarito numa etapa separada**, de preferência com o professor. Os nomes `caso_XX.png` são neutros; não utilizar o gerador de imagens para fornecer respostas ao agente.
6. **Calcular acertos e erros**, mantendo as previsões originais e investigando o processamento das imagens, as ativações e o modelo.
7. **Documentar resultados e hipóteses** com Issues, commits e evidências de testes.
8. Se modificar o modelo ou a aplicação depois de conhecer o gabarito, registrar uma **nova iteração**, sem substituir a avaliação inicial.

## Matriz de verificação

Registrar **PASS, FAIL, BLOCKED ou NOT RUN**, com evidências.

| Verificação | Evidência |
| --- | --- |
| Treinamento e teste MNIST | Pesos, logs, métricas reais e testes reproduzíveis |
| Paridade entre ambientes | Previsões compatíveis com o modelo de origem sobre a mesma entrada |
| Desenho no site | Área interativa e previsões produzidas pela rede |
| Upload das dez imagens | Dez miniaturas e dez classificações do modelo |
| Execução local | Inferência no navegador, sem backend de classificação |
| Visualização da rede | Valores e ativações reais, não animação decorativa |
| GitHub Pages | URL pública funcional |
| Integridade do desafio | Dez previsões registradas antes de comparar com rótulos |
| Rastreabilidade | Versão Git, pesos, Issues e registro de erros |

**Não declarar como concluído o que não foi executado.**

## Entregável

**Relatório de validação** com URL pública, commit, identificação dos pesos, resultados do MNIST, **dez previsões CAPTCHA**, total de acertos, análise de erros e evidências de que upload e inferência funcionaram.

**Próximo exercício:** [roda de feedback](../Exercicio-04-Roda-de-Feedback.md) com avaliação do professor, esclarecimento de dúvidas, pendências e correções com o agente.
