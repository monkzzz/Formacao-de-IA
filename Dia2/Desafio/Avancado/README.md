# Desafio avançado — 10 dígitos em estilo CAPTCHA

**Dez imagens PNG de 192 × 192 pixels**, uma de cada dígito de **0 a 9**, produzidas para testar os limites de uma rede treinada em imagens MNIST limpas. Trata-se de um desafio **visual**, não uma questão de nomenclatura de arquivos: cada previsão deve depender apenas dos pixels apresentados ao modelo.

## Por que estes exemplos são difíceis?

Um classificador MNIST normalmente vê **um único dígito isolado, centralizado e praticamente sem interferência**, em 28 × 28 pixels. Aqui, o algarismo aparece misturado a elementos que imitam a mesma tinta e prejudicam o pré-processamento:

| Interferência | O que acontece na imagem | Limitação investigada |
| --- | --- | --- |
| **Linhas sinuosas cruzadas** | 3 a 4 traços passam por dentro e fora do dígito, com cor parecida | O modelo pode confundir interferência com parte do algarismo |
| **Traços partidos** | Fissuras apagam partes reais do símbolo | Contornos e conexões internas deixam de ser contínuos |
| **Fragmentos de tinta** | Riscos soltos imitam pequenos pedaços de escrita | Recorte, centralização e segmentação podem incorporar ruído |
| **Deformação não linear** | Ondulações locais, rotação e caligrafias diferentes | A geometria já não corresponde diretamente às amostras MNIST |
| **Oclusões parciais** | Algumas regiões do contorno desaparecem | A rede precisa reconhecer informação incompleta |
| **Textura e cor** | Fundo levemente irregular, variações de tinta e pontos dispersos | Normalização de intensidade e separação de fundo podem falhar |

As deformações são **combinadas em cada imagem**, como acontece em muitos CAPTCHAs. Os números continuam destinados a ser reconhecíveis por uma pessoa, mas alguns casos podem ser ambíguos. **Não existe garantia de que um modelo específico errará todos eles.**

### Arquivos

Os dez PNGs estão diretamente nesta pasta, como `caso_01.png` até `caso_10.png`. O gerador determinístico está em [`gerar_desafio_avancado.py`](../gerar_desafio_avancado.py) e utiliza Pillow para construir os caracteres com cortes e sobreposições.

## Como avaliar

1. **Congele a versão do modelo e do site antes do teste.** Não utilize estes dez exemplos para treinar, selecionar hiperparâmetros ou escolher entre checkpoints.
2. Abra o GitHub Pages com a interface de **upload de imagens** e carregue os dez PNGs.
3. Registre a previsão bruta de cada imagem, as pontuações por classe e, se disponível, a imagem **após o pré-processamento**.
4. Compare com os rótulos somente depois que todas as previsões estiverem registradas. O código gerador permite auditoria, mas não deve ser usado como informação de entrada pelo agente durante o teste.
5. Separe os resultados: **teste oficial do MNIST**, **nove imagens originais do desafio** e **dez casos CAPTCHA** são baterias diferentes.
6. Investigue os erros: a rede reconheceu mal o glifo ou o pré-processamento tratou as linhas extras como parte do símbolo?

**Perguntas para a roda de feedback:** Quando a máscara de tinta inclui riscos cruzados, a centralização ainda é adequada? Uma rede mais robusta ou uma estratégia diferente de segmentação resolveria a falha? Se o símbolo fica visualmente ambíguo até para pessoas, faz sentido chamar a resposta da rede de errada com certeza?

O objetivo é **medir e explicar limitações reais**, não apresentar taxas inventadas. Repetir a avaliação após corrigir a rede é uma nova iteração, e não substitui o primeiro resultado independente.

## Pesquisa que fundamentou o desenho

- [AAAI 2026 — Improving CAPTCHA Robustness via Controlled Image Corruptions](https://ojs.aaai.org/index.php/AAAI/article/view/42290): deformação, ruído e oclusões com atenção à legibilidade.
- [Electronics 2025 — Revisiting Text-Based CAPTCHAs](https://www.mdpi.com/2079-9292/14/22/4403): combinações de distorções, multicamadas e elementos anti-reconhecimento.
- [Practicality analysis of text-based CAPTCHA authentication](https://pmc.ncbi.nlm.nih.gov/articles/PMC10152023/): deformações elásticas e compromisso com a legibilidade humana.

**[Voltar ao desafio](../)** · **[Exercício 3 — Parte 4](../../Exercicio-03/Parte-04-Teste-do-Desafio.md)**
