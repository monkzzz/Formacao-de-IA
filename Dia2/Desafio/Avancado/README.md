# Desafio avançado — 10 dígitos problemáticos

Esta pasta contém **dez imagens PNG de 160 × 160 pixels** representando, uma vez cada, os dígitos **0–9**, em ordem embaralhada. Foram construídas para expor limitações reais de classificação em imagens **diferentes do MNIST**.

São intencionalmente mais difíceis que os nove casos originais: incluem **rotação, mudança de escala, caligrafia irregular, fundos e tintas coloridos, baixo contraste, ruído, riscos distratores e oclusões parciais**.

## Desafio de avaliação

1. Treine e avalie normalmente a rede no [MNIST](../../Dataset-MNIST/README.md).
2. **Congele a versão do modelo e do site antes de testar os casos avançados.**
3. No site publicado do projeto, carregue **as dez imagens** pela funcionalidade de upload. Confira que nenhuma é enviada a um serviço remoto de inferência.
4. Registre **as dez previsões brutas**, a pontuação por classe e o comportamento do pré-processamento, antes de consultar qualquer rótulo.
5. Com o professor, confira os rótulos e investigue erros de domínio, contraste, rotação, segmentação, recorte, centralização ou confusão entre classes.
6. Mantenha o resultado **10 casos avançados** separado da acurácia nos **10.000 testes oficiais do MNIST** e do desafio original de **nove imagens**.

**Perguntas para a discussão:** o classificador erra por causa da rede ou porque a imagem carregada foi preparada de maneira inadequada? Os riscos são tratados como tinta? Qual é a evidência de que o modelo decidiu pelos pixels, não pelo nome do ficheiro? Melhorar um desses casos depois de conhecer o rótulo ainda constitui avaliação cega?

Os nomes \`caso_01.png\` etc. **não revelam os rótulos**, mas o código gerador está disponível no repositório para auditabilidade. Para uma avaliação sem consultar o gabarito, os participantes devem **evitar abrir o gerador e não alimentar o agente com os rótulos**, até registrar todas as previsões.

**Importante:** esta bateria é um *stress test* didático, não um ataque adversarial formal nem um benchmark estatisticamente representativo. As imagens foram feitas para serem difíceis, **não há garantia de que a rede erre todas elas**. Algumas podem ser ambíguas para pessoas; documente a divergência em vez de forçar uma resposta.

[Voltar ao desafio](../) · [Exercício 3 — Parte 4](../../Exercicio-03/Parte-04-Teste-do-Desafio.md)
