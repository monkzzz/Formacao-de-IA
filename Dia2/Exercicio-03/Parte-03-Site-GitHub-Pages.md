# Exercício 3 · Parte 3 — Criar o site no GitHub Pages

## Objetivo

Desenvolver, com o GitHub Copilot, uma **demonstração interativa da rede neural treinada na Parte 2**, semelhante em finalidade ao [Image-classifier-demo](https://github.com/vcanonici/Image-classifier-demo), mas com uma funcionalidade adicional **obrigatória: carregar imagens do computador para classificá-las**.

A aplicação deverá ser publicada no **GitHub Pages** e executar a inferência **inteiramente no navegador**, utilizando os pesos do modelo realmente treinado. Nenhuma imagem poderá depender de uma API de classificação ou backend remoto durante a inferência.

## Analise primeiro o repositório de referência

Examine o [Image-classifier-demo](https://github.com/vcanonici/Image-classifier-demo) com o Copilot. Observe os componentes responsáveis por:

- Área de desenho com mouse, caneta ou toque e opção para limpar.
- Apresentação da previsão e das pontuações para as classes 0 a 9.
- Visualização dos pixels de entrada, das camadas, ativações e conexões reais da rede neural.
- Pré-processamento da imagem, carregamento dos pesos e inferência executada em código no navegador.
- Testes, comparação entre runtimes e publicação no GitHub Pages.

**Não reinvente a roda:** é permitido pesquisar, reaproveitar e adaptar componentes úteis do exemplo, respeitando a licença e atribuindo a origem. **Remova ou substitua o que não servir**: identidade visual, regras do projeto original, dependências desnecessárias e pressupostos sobre uma arquitetura particular.

A rede do exemplo tem uma topologia específica e um formato particular de pesos. **Você não é obrigado a reproduzi-los**: a interface e o processamento deverão refletir a rede escolhida e treinada no **seu** projeto.

## Perguntas socráticas para projetar o site

### Interação

- Como uma pessoa poderá desenhar um dígito, apagar e tentar novamente?
- Como indicar claramente qual dígito foi previsto e quais foram os escores das outras classes?
- Que informação real da rede ajudaria alguém a compreender **por que a resposta surgiu**, sem fingir explicar mais do que o modelo permite observar?

### Novo requisito: upload de imagens

- Como permitir que o usuário **selecione uma ou várias imagens locais** (por exemplo, PNG ou JPEG) e veja sua pré-visualização?
- Como classificar **cada imagem carregada** e identificar o resultado correspondente, sem perder a opção de desenhar no canvas?
- Uma imagem enviada pode ter fundo colorido, dimensões diferentes, margens ou dígitos em cores variadas. O que deve acontecer no pré-processamento?
- Como garantir que **o desenho e o upload atravessem um fluxo de preparação coerente** antes de chegar à mesma rede neural?
- Como lidar com arquivo inválido, imagem vazia, formato não suportado ou falha de leitura?
- Os nomes dos arquivos do [desafio](../Desafio/) indicam a classe verdadeira. Como garantir que **somente os pixels**, e nunca o nome ou um rótulo fornecido externamente, determinem a previsão?

**Requisito mínimo:** aceitar imagens locais de modo utilizável e permitir processar as **nove imagens do desafio** (individualmente ou em seleção múltipla), mostrando **uma previsão verificável para cada arquivo**, com pré-visualização, classe prevista e pontuações do modelo.

O upload pode ser realizado por um controle de seleção de arquivos; arrastar e soltar é opcional. **O arquivo não deve ser enviado para um servidor de inferência.**

### Integração e publicação

- Como comprovar que o site carrega exatamente os pesos treinados na Parte 2?
- A inferência no navegador e a inferência feita no treinamento fornecem resultados compatíveis sobre a mesma entrada?
- Quais transformações da imagem precisam ser replicadas nos dois ambientes?
- Uma visualização da rede reflete **ativação e conexões verdadeiras** ou é apenas animação decorativa?
- Como provar que a aplicação publicada funciona no GitHub Pages, fora do computador do aluno?

## Como desenvolver com o agente

Utilize as **Issues específicas do site** criadas na Parte 1; atualize-as se a análise da referência revelar dependências, riscos ou verificações que faltam. Implemente em unidades pequenas, com revisão de diff e testes.

Verifique separadamente: desenho; upload de arquivos; pré-processamento; inferência; visualização real da rede; integração dos pesos; compatibilidade entre treinamento e web; publicação no GitHub Pages.

**O agente deve programar e testar a aplicação**. Seu papel é direcionar, decidir o que reaproveitar e verificar que os recursos funcionam.

## Entregável da parte 3

**URL pública do GitHub Pages** com uma aplicação que:

- Permite desenhar e classificar dígitos.
- Permite **carregar imagens locais**, individualmente ou em conjunto, e classificá-las.
- Mostra resultados e informações reais sobre a rede.
- Usa os **pesos treinados no projeto**, com inferência local no navegador.
- Funciona sem servidor remoto de classificação.

**Ponto de verificação:** carregar uma imagem local e comparar sua previsão com a obtida pelo código de avaliação da rede, quando aplicada a mesma transformação de entrada. A interface deverá refletir o modelo verdadeiro, não um resultado estático.
