# Exercício 1 — Crie seu próprio starter repository para trabalhar com agentes

## O desafio

Ao longo da formação, você aprendeu o conceito de **starter repository**. Agora deverá **conceber e construir o seu próprio**, utilizando o **GitHub Copilot no VS Code, em modo agente**.

Pense nesta situação: amanhã você inicia um projeto completamente diferente do atual. Você quer abrir um repositório e começar a trabalhar com um agente que **já conheça sua forma preferida de desenvolver software** — como investigar, planejar, modificar código, validar resultados, usar Git, documentar decisões e retomar trabalho de sessões anteriores.

**Como criar um ponto de partida que torne isso possível sem explicar tudo novamente em cada conversa?**

Este é o problema do exercício.

**Não será fornecido um starter repo, uma árvore de diretórios para copiar, um template ou um arquivo de instruções pronto.** A arquitetura do repositório, os documentos e as regras serão decididos por você, em colaboração com o Copilot.

> As perguntas a seguir são **perguntas socráticas para orientar suas decisões**, não prompts prontos para copiar e colar no agente. Use-as para investigar os problemas, discutir alternativas com o Copilot e construir sua própria solução.

## 1. Descubra o que deve sobreviver de um projeto para outro

Antes de criar arquivos, pense em **como você gostaria de trabalhar com um coding agent**.

- Quando você começa um projeto novo, que explicações acaba repetindo ao agente?
- Quais dessas explicações descrevem **sua maneira de trabalhar**, e quais dependem do projeto específico?
- Se você mudar de linguagem, framework ou tipo de aplicação, quais regras devem continuar válidas?
- O que diferencia um agente que apenas escreve código de outro que trabalha **da forma que você considera correta**?
- Como o agente poderia descobrir suas preferências sem depender do histórico de uma conversa anterior?

**Sua tarefa:** com o Copilot, identificar quais princípios, preferências e limites devem estar presentes em qualquer projeto iniciado com seu starter repo.

Não escolha ainda uma stack para o classificador de dígitos. O objetivo é preparar um **ambiente genérico**, não antecipar o projeto dos próximos exercícios.

## 2. Pense no contexto como um sistema, não como um arquivo gigante

O agente precisa conhecer algumas regras em todas as tarefas. Outras informações só importam em situações específicas.

- Que informações o agente deveria consultar **sempre**, antes de trabalhar?
- O que aconteceria se todas as instruções, procedimentos e referências fossem colocados no mesmo arquivo?
- Como o agente descobriria **qual procedimento especializado** consultar diante de uma tarefa nova?
- Qual a diferença entre uma **regra de atuação**, uma **decisão de projeto**, um **procedimento operacional** e um **registro de algo aprendido**?
- Se uma decisão técnica mudar, onde ela deve ser atualizada para evitar orientações contraditórias?
- Como organizar essas informações de modo que o agente encontre o necessário **sem carregar conteúdo irrelevante**?

**Sua tarefa:** discutir com o Copilot uma arquitetura de contexto que combine **orientação persistente** com **informação consultada quando necessária**. Escolha e justifique a estrutura de arquivos e pastas.

Você poderá utilizar convenções conhecidas, como instruções persistentes para agentes, mas **deverá decidir o que escrever, onde guardar e como os documentos se relacionam**.

## 3. Ensine ao agente seu método de trabalho

Imagine que você pede uma alteração aparentemente simples. O agente começa a editar imediatamente e, no final, afirma que concluiu.

- O que ele deveria investigar **antes da primeira alteração**?
- Como poderia identificar os arquivos afetados e evitar mudanças não relacionadas?
- Você prefere aprovar um plano antes da implementação? Em quais situações?
- Que evidências seriam suficientes para acreditar que o trabalho realmente funciona?
- Se um teste falhar, o que o agente deve fazer? E se não existir teste?
- Como evitar que o agente diga que validou algo **sem ter executado a validação**?
- Que parte desse método deveria valer para **todo projeto**, independentemente da linguagem?

**Sua tarefa:** definir com o Copilot um **modo de operação reutilizável**, do entendimento da tarefa até a verificação e o registro do resultado. Faça o agente materializar essas regras no starter repo.

Não basta escrever que o agente deve “produzir código de qualidade”. Pense **como o comportamento esperado poderá ser observado e verificado**.

## 4. Decida como preservar trabalho e registrar decisões

Agora considere que o agente trabalha em um repositório com mudanças existentes, histórico Git e conhecimento adquirido em sessões anteriores.

- Como impedir que ele apague, substitua ou versione alterações que não pertencem à tarefa?
- Que operações de Git podem ser executadas normalmente e quais deveriam exigir autorização?
- Como relacionar uma mudança ao problema que ela resolve?
- Se o agente descobriu a causa de um erro difícil, **onde registrar esse conhecimento** para não investigar tudo novamente?
- Uma conclusão inferida pelo agente deveria ser registrada da mesma maneira que um fato comprovado por teste?
- Que informações precisam ser guardadas para que outra sessão consiga continuar o trabalho?
- Como evitar que registros antigos se tornem regras falsas ou desatualizadas?

**Sua tarefa:** estabelecer práticas de versionamento, rastreabilidade e preservação de conhecimento. Pedir ao Copilot que implemente no starter repo os mecanismos documentais que considerar adequados.

Considere a diferença entre **o que aconteceu**, **o que foi decidido** e **o que será útil reutilizar no futuro**.

## 5. Prepare o agente para utilizar ferramentas sem presumir capacidades

Em projetos futuros, o agente poderá precisar de skills, comandos de terminal, serviços externos ou servidores MCP.

- Como ele vai saber quais ferramentas **estão realmente disponíveis** no computador?
- Como distinguir uma ferramenta **necessária**, uma ferramenta **desejada** e uma já **instalada e validada**?
- Que informações devem ser registradas para usar uma capacidade com segurança: finalidade, entradas, saídas, dependências, riscos, condições de uso?
- Como o agente deveria proceder quando uma ferramenta de que precisa **não está disponível**?
- Quando é melhor ter uma instrução geral e quando faz sentido criar uma **skill** ou procedimento especializado?
- Onde ficariam os requisitos de configuração de uma integração sem expor tokens ou segredos no Git?

**Sua tarefa:** projetar uma maneira de **descobrir, documentar e verificar capacidades** do ambiente. Não é necessário instalar ferramentas ou servidores MCP apenas para preencher uma estrutura.

No **Exercício 2**, você criará uma skill própria. Por enquanto, seu starter repo deve estar preparado para **receber e organizar habilidades futuramente**, sem conter essa implementação pronta.

## 6. Pense em como o starter repo começa um projeto novo

O repositório que você está criando **ainda não conhece o projeto que será desenvolvido**. Isso é intencional.

- O que deveria permanecer intacto quando o starter repo fosse utilizado para um novo projeto?
- Que informações ainda precisariam ser descobertas sobre esse projeto?
- Quem deve decidir requisitos e restrições: o agente sozinho ou a pessoa responsável?
- Como transformar respostas obtidas em conversa em **contexto persistente**, em vez de deixá-las perdidas no chat?
- Como o agente distinguirá instruções genéricas do starter repo das decisões específicas de cada projeto?
- Como impedir que preferências ou configurações de um projeto anterior contaminem o seguinte?
- Se o projeto mudar de direção, como atualizar o contexto sem perder decisões relevantes?

**Sua tarefa:** deixar o starter repo **preparado para ser contextualizado** quando um novo trabalho começar.

**Não desenvolva agora um mecanismo de entrevista ou uma skill de bootstrap.** Esse será o desafio do Exercício 2: criar uma skill inspirada na lógica *Ask Me* para coletar requisitos e popular a estrutura que você construir aqui.

## 7. Construa o repositório com o Copilot

Com base nas decisões anteriores:

1. Crie um **novo repositório GitHub próprio e vazio** e abra-o no VS Code com GitHub Copilot em modo agente.
2. Discuta com o agente **quais problemas sua estrutura precisa resolver** e quais alternativas fazem sentido.
3. Avalie o desenho proposto. Pergunte a si mesmo se cada documento ou diretório possui uma responsabilidade clara.
4. **Autorize o Copilot a criar** as instruções, os procedimentos, a organização do contexto e a documentação decididos.
5. Revise o resultado: os arquivos realmente explicam como o agente deve agir ou são apenas pastas e textos genéricos?
6. Faça os ajustes necessários, confira o estado Git e **versione a solução**.

**O Copilot deve ajudar a projetar e criar os arquivos.** Você deve tomar decisões e verificar que a estrutura produzida funciona como pretende.

## 8. Ponha o starter repo à prova

Uma estrutura bonita não demonstra que um agente consegue utilizá-la.

**Experimento A — Continuidade entre sessões**

Encerre a conversa e abra outra no VS Code, mantendo o repositório. Sem reexplicar suas preferências:

- O agente consegue identificar como você prefere que ele trabalhe?
- Consegue localizar as instruções e procedimentos relevantes?
- Sabe o que precisa verificar antes de alterar um arquivo?
- Sabe onde registrar uma decisão técnica ou um aprendizado?
- Reconhece seus limites e sabe quando deve perguntar?

**Experimento B — Reutilização em outro projeto**

Imagine um projeto novo, diferente do classificador que será desenvolvido depois:

- Que partes do starter repo continuariam úteis sem alteração?
- O que precisaria ser preenchido com informações desse novo projeto?
- Há regras ou dependências específicas demais que não deveriam estar na estrutura genérica?
- Seu starter repo conseguiria servir a projetos diferentes sem carregar pressupostos incompatíveis?

**Experimento C — Autonomia e verificação**

Proponha ao agente uma pequena tarefa segura relacionada **ao próprio starter repo**, como revisar documentação ou identificar uma inconsistência.

- Ele consulta o contexto antes de agir?
- Aplica o procedimento que você definiu?
- Mostra o que alterou e como verificou o resultado?
- Respeita as regras de versionamento e autorização?

Se alguma resposta não corresponder ao comportamento desejado, **revisite suas decisões e refine o repositório**.

## Entregável

**Um starter repository original, genérico e reutilizável**, construído do zero pelos participantes com GitHub Copilot, publicado em seu próprio GitHub e contendo:

- Uma forma clara de comunicar ao agente **como o participante quer trabalhar**.
- Uma organização de contexto persistente e procedimentos consultáveis conforme a necessidade.
- Regras de planejamento, execução, validação, segurança e versionamento.
- Um método de registrar conhecimento e decisões reutilizáveis.
- Uma forma de documentar capacidades do ambiente, como skills, CLI tools e MCPs.
- Documentação que permita usar e evoluir o starter repo.
- Evidências dos testes de **nova sessão, reutilização e comportamento do agente**.

**Critério de sucesso:** o starter repo não deve ser avaliado pela quantidade de pastas, mas por sua capacidade de fazer o agente **trabalhar de maneira consistente com as regras escolhidas pelo aluno, em diferentes projetos e conversas**.

**O que ainda não deve existir:** skill de bootstrap pronta, Issues do classificador, dataset, arquitetura da rede neural, treinamento ou site.

**Próxima etapa:** no Exercício 2, você criará uma skill de bootstrap que utiliza perguntas para descobrir o contexto de um projeto e **popula este starter repo**, preservando as regras gerais que você definiu.
