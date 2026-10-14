# Exercício 4 — Roda de feedback: avaliação, dúvidas e correções

## Objetivo da atividade

Participar de uma **roda de feedback conduzida pelo professor**, na qual as aplicações desenvolvidas no Exercício 3 serão testadas, discutidas e aperfeiçoadas.

O foco não é fazer uma apresentação formal de um projeto supostamente perfeito. É **mostrar o que realmente funciona, esclarecer dúvidas, identificar pendências, receber sugestões e realizar correções com o GitHub Copilot no VS Code**. Os participantes também devem aprender com os problemas e as soluções apresentados pelos colegas.

## Material de partida

Cada participante deverá ter disponível:

- Seu repositório GitHub, iniciado com o starter repo construído no Exercício 1.
- A skill de bootstrap criada no Exercício 2 e o contexto do projeto registrado por ela.
- As GitHub Issues e o histórico das alterações realizadas com o agente.
- A rede treinada, as evidências de avaliação no MNIST e os pesos utilizados no site.
- A **URL do GitHub Pages**, com desenho e upload de imagens, e o registro das previsões das nove imagens do desafio.

Se algo não estiver pronto, **apresente a situação real** e identifique o que falta. Uma pendência assumida e investigada também faz parte da aprendizagem.

## 1. Professor e turma experimentam as aplicações

Cada participante disponibiliza a URL pública e mostra o funcionamento de sua aplicação. O **professor avalia o app diretamente**, em vez de depender apenas da descrição do aluno ou do agente.

A avaliação deve considerar:

- A interface permite desenhar dígitos, limpar o desenho e classificá-lo?
- É possível **carregar imagens locais**, inclusive as nove imagens do desafio, e obter uma previsão para cada uma?
- A classificação é produzida pela rede **realmente treinada pelo participante**, executando no navegador sem API de inferência?
- As pontuações e a visualização apresentada correspondem a informações reais do modelo?
- O site publicado funciona adequadamente, ou existem falhas de carregamento, de interação ou de pré-processamento?
- O resultado reportado para o **teste oficial do MNIST** está separado do resultado das **nove imagens do desafio**?

**Perguntas para orientar a observação:** o que acontece quando uma imagem diferente é carregada? A previsão acompanha o conteúdo visual? O app consegue mostrar limitações, em vez de apenas aparentar funcionar?

## 2. Roda de dúvidas e feedback coletivo

Depois de testar cada aplicação, o professor abre espaço para que o participante e os colegas discutam **dúvidas técnicas, decisões, obstáculos e soluções**.

Algumas questões para orientar a conversa:

- Qual foi a decisão mais difícil durante o planejamento ou o treinamento?
- Que tarefa o agente conseguiu executar corretamente? Onde ele precisou ser corrigido?
- Que problema apareceu apenas quando o modelo foi integrado ao site?
- O pré-processamento das imagens carregadas produz entradas compatíveis com as utilizadas no treinamento?
- O que os erros da rede mostram sobre os dados, a arquitetura e o processo de validação?
- Que orientação, procedimento ou informação faltou ao agente e deveria ficar registrada no starter repo?
- Alguma solução vista no trabalho de outro participante pode ser **reaproveitada ou adaptada**, evitando reinventar a roda?

O objetivo é que **o feedback seja útil para toda a turma**, não apenas para quem está demonstrando o aplicativo. Evitar comparações superficiais baseadas somente na aparência do site ou no número de acertos.

## 3. Identificar pendências e realizar correções

Com base nos testes e no feedback do professor, cada participante deverá:

1. **Distinguir os problemas observados** das hipóteses sobre suas causas.
2. Registrar correções e melhorias necessárias como **GitHub Issues**, ou atualizar Issues já existentes.
3. Priorizar o que compromete o funcionamento ou os critérios essenciais: carregamento do modelo, desenho e upload, inferência no navegador, publicação, visualização verdadeira e rastreabilidade.
4. **Pedir ao GitHub Copilot que investigue e corrija** as pendências escolhidas, respeitando os procedimentos do seu starter repo.
5. Executar testes e comparar o comportamento **antes e depois da alteração**, quando possível.
6. Revisar o diff, registrar os resultados e criar commits relacionados às Issues.
7. Identificar o que foi resolvido e o que continua pendente, sem declarar concluída uma correção não verificada.

**Perguntas durante a correção:** a mudança trata a causa do problema ou apenas esconde o sintoma? Que evidência comprova a melhoria? O agente alterou somente o necessário? A correção introduziu outro problema?

Nem todas as pendências precisam desaparecer durante a roda. O essencial é **saber explicá-las, priorizá-las e registrar o próximo passo**.

## 4. Preservar a honestidade da avaliação

Se uma correção alterar o modelo, o pré-processamento ou o site **depois de conhecer os resultados das nove imagens**, ela constitui uma **nova iteração**.

- Conservar o resultado original e a versão em que ele foi obtido.
- Registrar separadamente o resultado após as correções, caso as imagens sejam testadas novamente.
- Não substituir previsões anteriores nem apresentar uma melhoria posterior como se fosse a primeira avaliação independente.
- Não confundir **9/9 no desafio** com garantia de generalização em outros dados.

## Resultado da atividade

Ao final da roda, cada participante deverá deixar no próprio repositório um **registro breve do feedback**, contendo:

- O que o professor efetivamente testou e observou na aplicação.
- As dúvidas discutidas e os esclarecimentos mais relevantes.
- Os problemas, limitações e pendências identificados.
- As **Issues criadas ou atualizadas** para tratar o feedback.
- Quais correções foram implementadas com o agente, com **commits e evidências de validação**, e quais ainda estão abertas.
- A URL do app e, quando houver correções publicadas, a identificação da versão atual.

**Critério central:** demonstrar capacidade de **receber feedback, investigar problemas reais e evoluir uma aplicação com o coding agent**, preservando evidências e aprendendo com o trabalho coletivo.
