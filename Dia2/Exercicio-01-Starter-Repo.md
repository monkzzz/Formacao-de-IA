# Exercício 1 — Criar seu próprio starter repository para coding agents

## Objetivo da atividade

**Construir do zero, com a ajuda do GitHub Copilot no VS Code, um starter repository próprio e reutilizável**, preparado para receber projetos de software desenvolvidos por agentes de IA.

O professor forneceu um exemplo de **Starter Repo** para mostrar o tipo de infraestrutura esperado. **O exemplo não é uma solução para copiar, clonar ou simplesmente adaptar.** Cada participante deverá investigar sua organização, compreender por que os componentes existem, decidir como estruturar o seu repositório e **pedir ao Copilot que o construa**.

Neste exercício, a tarefa é **criar o ambiente de trabalho do agente**, não desenvolver o classificador de dígitos.

## O que é um starter repository neste exercício?

É um repositório que funciona como **ponto de partida para diferentes projetos futuros**. Ele contém instruções e mecanismos de organização para que um coding agent consiga:

- Compreender seu papel e as regras gerais do repositório.
- Descobrir onde procurar o contexto relevante de uma tarefa.
- Consultar procedimentos especializados somente quando necessários.
- Registrar decisões, documentação e conhecimento reutilizável.
- Identificar skills, ferramentas e integrações disponíveis ou desejadas, sem presumir que já estejam instaladas.
- Planejar, executar, verificar e registrar alterações de forma rastreável.
- Retomar o trabalho em uma nova conversa sem depender de todo o histórico do chat.

**O repositório deve estar pronto para receber um projeto, mas ainda não deve conter a solução desse projeto.**

## Material de referência

Analisar o exemplo de Starter Repo apresentado pelo professor. Nele, dois elementos têm papéis diferentes:

- **`AGENTS.md`** atua como um contrato operacional do agente: regras sempre relevantes, prioridades e indicação de onde localizar instruções mais detalhadas.
- **`AgentDATA/`** organiza informações e recursos que não precisam ocupar permanentemente o contexto do agente: documentação, procedimentos, conhecimento, referências, registros, skills e ferramentas.

Observar também como o exemplo distingue **procedures**, **skills**, **MCP servers** e **CLI tools**, e como propõe consultar apenas os recursos relevantes para cada tarefa.

Não é obrigatório reproduzir exatamente os mesmos nomes, a mesma quantidade de diretórios ou todos os procedimentos do exemplo. É obrigatório, porém, **construir uma estrutura própria que resolva esses problemas de organização** e conseguir justificar as decisões.

## Ficha de requisitos

Com o GitHub Copilot no **VS Code em modo agente**, os participantes deverão:

### 1. Investigar e planejar a estrutura

- Criar um **novo repositório GitHub próprio**, inicialmente vazio.
- Examinar o exemplo apresentado e identificar quais problemas cada componente procura resolver.
- Discutir com o Copilot quais componentes são necessários para um starter repo genérico e quais seriam excessivos.
- Definir uma organização coerente de arquivos, pastas, documentos e índices **antes de solicitar sua criação**.

### 2. Criar o contrato de trabalho do agente

- Construir um arquivo de instruções para o agente, como `AGENTS.md`.
- Estabelecer como o agente deve iniciar uma tarefa, consultar o repositório e identificar o contexto relevante.
- Definir como planejar alterações, verificar resultados e registrar trabalho concluído.
- Distinguir **regras gerais** de **procedimentos específicos**, evitando concentrar tudo em um único documento extenso.
- Determinar quais ações precisam de revisão ou autorização humana.

### 3. Organizar a base de contexto e conhecimento

Criar uma estrutura própria, inspirada nas finalidades presentes no exemplo, que permita organizar:

- **Contexto:** objetivos, informações operacionais e decisões de projetos que venham a utilizar o starter repo.
- **Documentação e referências:** materiais que o agente poderá consultar.
- **Conhecimento e memória de trabalho:** aprendizados e informações relevantes para sessões futuras.
- **Procedimentos:** instruções de execução e verificação que possam ser carregadas quando uma tarefa exigir.
- **Registros:** histórico útil de decisões, mudanças, execuções e problemas.
- **Skills:** local de documentação e descoberta das capacidades especializadas do agente.
- **Ferramentas e MCPs:** inventário de capacidades disponíveis, dependências, limitações e condições de uso.
- **Informações sensíveis:** regras para impedir que segredos e credenciais reais sejam versionados.

A organização pode utilizar uma pasta como `AgentDATA/`, tal como o exemplo, ou outra solução justificada pelo participante. **Não basta criar pastas vazias:** os arquivos de orientação devem explicar a finalidade de cada parte e como o agente a utiliza.

### 4. Definir procedimentos reutilizáveis

Com a ajuda do Copilot, criar procedimentos genéricos que façam sentido num repositório destinado ao desenvolvimento com agentes, considerando, por exemplo:

- Como iniciar uma tarefa e reunir contexto.
- Como planejar modificações antes de executá-las.
- Como validar mudanças e lidar com falhas.
- Como revisar diffs e realizar commits.
- Como documentar decisões e registrar conhecimentos úteis.
- Como descobrir e utilizar recursos especializados, sem presumir sua disponibilidade.

O participante deverá decidir **quais procedimentos efetivamente incluir, como documentá-los e quando o agente deve consultá-los**.

### 5. Preparar o repositório para as próximas atividades

- Criar um `README.md` que explique o que é o starter repo, como utilizá-lo e como está organizado.
- Deixar claro quais informações ainda precisarão ser fornecidas quando um projeto concreto começar.
- Considerar como o starter repo poderá receber **uma skill de bootstrap baseada em perguntas**, que será criada **no Exercício 2**.
- Verificar se as instruções da estrutura criada são compatíveis com o GitHub Copilot no VS Code, distinguindo um **catálogo de skills** da localização que o Copilot reconhece para executar skills nativas.
- Versionar a estrutura criada e registrar um commit identificável.

**Não criar agora a skill de bootstrap, a rede neural, o treinamento, o dataset, as Issues do classificador nem o site.** Essas são atividades seguintes.

## Como verificar o resultado

Após criar o starter repo:

1. Examinar com o Copilot se a documentação e a organização são coerentes e se há instruções contraditórias ou arquivos sem função clara.
2. **Encerrar a conversa e abrir outra** no VS Code, com o repositório disponível.
3. Verificar se o agente consegue entender **a finalidade do starter repo**, suas regras, a organização dos recursos e como deverá iniciar um futuro projeto.
4. Identificar informações que não foram recuperadas, dependências presumidas ou procedimentos confusos e **refinar a estrutura**, se necessário.

A verificação não consiste apenas em contar arquivos e diretórios: é preciso comprovar que **o agente consegue utilizar o repositório como infraestrutura de trabalho**.

## Entregável

**Um starter repository próprio, criado do zero com o GitHub Copilot, publicado no GitHub e versionado**, contendo:

- Contrato operacional do agente.
- README com explicação da organização.
- Estrutura para contexto, documentação, conhecimento, procedures, registros, skills e ferramentas.
- Procedimentos reutilizáveis e critérios de verificação.
- Orientações para uso e evolução da estrutura.
- Evidência de que o agente compreende o repositório em uma nova conversa.

**Resultado esperado:** um starter repo de propósito geral, comparável **em função e organização** ao exemplo mostrado pelo professor, mas projetado e construído pelos próprios participantes.

**Próximo exercício:** criar uma skill de bootstrap no estilo **Ask Me** para entrevistar o usuário sobre o projeto de classificação de dígitos e **popular esse starter repo com contexto específico**, sem recriá-lo do zero.
