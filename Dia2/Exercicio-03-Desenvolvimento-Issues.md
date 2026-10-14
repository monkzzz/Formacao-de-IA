# Exercício 3 — Do planejamento ao teste do classificador

## Desafio integrador

Utilize **o seu starter repo** (Exercício 1) e o contexto obtido com **a skill de bootstrap que você criou** (Exercício 2) para orientar o **GitHub Copilot no VS Code, em modo agente**, a desenvolver uma rede neural capaz de reconhecer dígitos manuscritos.

A solução será desenvolvida em **quatro partes encadeadas**. Não comece por pedir ao agente que implemente tudo. Primeiro, ele deverá investigar o problema, propor uma arquitetura e **criar GitHub Issues para o projeto inteiro**. Você revisará e aprovará essas Issues. A partir delas, o agente fará o trabalho de programação, treinamento, testes, desenvolvimento web e publicação.

| Parte | Atividade | Resultado |
| --- | --- | --- |
| [1 — Planejamento da rede neural](Exercicio-03/Parte-01-Planejamento-da-Rede.md) | Investigar requisitos, alternativas, dados, arquitetura e decompor o trabalho em Issues | Especificação e GitHub Issues aprovadas |
| [2 — Coding com o agente](Exercicio-03/Parte-02-Coding-com-o-Agente.md) | Implementar, treinar, testar e avaliar a rede com o Copilot | Modelo treinado, pesos, testes e métricas |
| [3 — Site no GitHub Pages](Exercicio-03/Parte-03-Site-GitHub-Pages.md) | Criar uma demonstração inspirada no Image-classifier-demo, **adicionando upload de imagens** | Site público com desenho, upload e inferência no navegador |
| [4 — Funciona com o test set?](Exercicio-03/Parte-04-Teste-do-Desafio.md) | Avaliar o modelo com os **dez dígitos CAPTCHA oficiais** no site publicado | Dez previsões verificáveis e diagnóstico de erros |

## Recursos disponíveis

- **[MNIST](Dataset-MNIST/README.md):** 60.000 imagens de treino e 10.000 de teste, com rótulos de 0 a 9. É o dataset de referência obrigatório para treinar e avaliar a rede.
- **[Dez imagens oficiais do desafio](Desafio/Avancado/README.md):** dígitos 0–9 com linhas cruzadas, traços interrompidos, fragmentos e deformações no estilo CAPTCHA; usar **somente na Parte 4**, sem treino ou ajuste. A classificação deve vir dos pixels, nunca dos nomes, rótulos ou do código gerador.
- **[Image-classifier-demo](https://github.com/vcanonici/Image-classifier-demo):** exemplo funcional com desenho, upload de imagens, visualização e inferência no navegador. Analisar e reutilizar/adaptar apenas o que fizer sentido; não copiar a arquitetura automaticamente.

## Regras de trabalho

- **Sem prompts prontos e sem uma solução de rede neural predefinida.** O exercício ensina a dirigir um agente, tomar decisões e verificar resultados.
- **Reaproveitar quando fizer sentido; não copiar indiscriminadamente.** Documentar o que foi adaptado de terceiros e respeitar suas licenças.
- **GitHub Issues antes do código.** Cada Issue deverá definir o que fazer, dependências, critérios de aceitação e verificações.
- **Plan → Exec → Verify → Review → Commit.** Implementar e validar por tarefas, sem alterar silenciosamente o escopo.
- **Inferência no navegador.** O GitHub Pages hospedará a aplicação estática e os artefatos do modelo treinado. A imagem desenhada ou carregada não deverá ser enviada a um servidor de classificação.
- **Avaliação honesta.** Métricas e previsões devem ser resultado de execuções reais. O desempenho no teste oficial do MNIST e o resultado nos dez PNGs CAPTCHA são avaliações distintas.

**Entrega final:** um único repositório próprio, com Issues, rede treinada, resultados, aplicação web pública e evidências de que o sistema realmente classifica as imagens.
