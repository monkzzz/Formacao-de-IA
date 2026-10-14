# Guia — Skills nativas do GitHub Copilot no VS Code

Este guia ensina **como criar e utilizar uma Agent Skill local**, sem `npx`, sem instalação de gerenciadores de skills e sem bibliotecas especiais para o mecanismo de skills.

## O que é uma skill

Uma Agent Skill é uma pasta com um arquivo **`SKILL.md`**, contendo metadados e instruções para um fluxo de trabalho especializado. O GitHub Copilot no **VS Code em modo agente** pode descobrir a skill e carregar seu conteúdo quando a tarefa for pertinente. Ela **não é um plugin executável** por si só nem precisa conter scripts.

## Criar uma skill do zero

1. No VS Code, abrir o **repositório do aluno** e verificar que o GitHub Copilot e o modo agente estão disponíveis.
2. Criar a pasta **`.github/skills/`** na raiz do projeto e, dentro dela, outra pasta com o nome escolhido para a skill.
3. Criar o arquivo **`SKILL.md`** nessa pasta. Ele deve ter um cabeçalho YAML com **`name`** (nome minúsculo, com hífens) e **`description`** (o que a skill faz e quando o agente deve utilizá-la).
4. Escrever abaixo do cabeçalho as **instruções de comportamento**, condições de uso, verificações e limites. Os alunos devem criar o conteúdo para o objetivo de sua skill; **não há prompt pronto para reproduzir**.
5. Salvar o arquivo, utilizar o menu de configuração de skills do Copilot, quando disponível, e verificar se a skill aparece. Algumas versões oferecem **`/skills`** ou **Chat: Open Customizations**.
6. Abrir uma nova conversa em modo agente e **testar o comportamento**. Diferenciar "o agente disse que conhece a skill" de "o agente seguiu efetivamente as instruções".
7. Refinar a skill e versionar os arquivos em Git. Replicar a pasta em outros projetos quando pertinente, respeitando direitos e licenças.

A estrutura mínima é:

    meu-repositorio/
    └── .github/
        └── skills/
            └── minha-skill/
                └── SKILL.md

O arquivo começa com um cabeçalho como:

    ---
    name: minha-skill
    description: Descreva a finalidade e quando esta skill deve ser utilizada.
    ---

O participante deverá **escrever a lógica da skill** a partir do Exercício 2. O exemplo ensina somente o formato, não resolve o bootstrap.

**Importante:** no starter repo de referência, `AgentDATA/skills/` é um **catálogo interno**. O Copilot não deve ser considerado capaz de descobrir automaticamente skills ali. A localização nativa recomendada para o projeto é `.github/skills/` (alternativas suportadas incluem `.agents/skills/` e `.claude/skills/`).

## Skill Ask Me disponível

A skill didática **`ask-me`** está incluída nesta formação: [abrir arquivo](../.github/skills/ask-me/SKILL.md).

Para usá-la **no repositório pessoal do aluno**, copiar manualmente a pasta **`ask-me/`** para **`.github/skills/ask-me/`** na raiz desse repositório. Não há instalação por `npx`, dependência Node.js ou script.

**Esta skill não é o exercício resolvido.** Ela apresenta um padrão genérico de entrevista. O Exercício 2 pede que cada participante crie uma **nova skill de bootstrap**, capaz de converter a entrevista em documentação e contexto persistente no starter repo.

## Skill shops e referências públicas

Pesquisar alternativas, estudar padrões de documentação e avaliar compatibilidade:

- [skills.sh](https://skills.sh/) — diretório comunitário de Agent Skills.
- [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) — coleções de customizações e skills relacionadas ao GitHub Copilot.
- [MicrosoftDocs Agent Skills](https://github.com/MicrosoftDocs/Agent-Skills) — exemplos e especializações da Microsoft.
- [Anthropic Skills](https://github.com/anthropics/skills) — exemplos de skills e estrutura de recursos.
- [OpenAI Skills](https://github.com/openai/skills) — catálogo de skills.
- [Official Skills](https://officialskills.sh/) — diretório de skills atribuídas a fornecedores.
- [Agent Skills — especificação](https://agentskills.io/) — padrão e formato, **não é uma loja de skills**.
- [Ask Me — exemplo de comunidade](https://www.skills.sh/dimabytes/skills-lib/ask-me) — referência conceitual para entrevistas.

**As páginas de catálogos frequentemente mostram comandos `npx skills add`: eles são opcionais.** Nesta formação, podem ser usados **apenas para descobrir o nome, a documentação e os arquivos necessários**. Os alunos devem criar ou copiar skills **diretamente no VS Code**, sem executar instaladores desconhecidos.

## Cuidados

- Verificar fonte, licença e segurança antes de copiar skills de terceiros. Skills são **instruções executadas pelo agente**, podendo induzir acesso a arquivos ou ferramentas.
- Não dar aprovação irrestrita a comandos, ações destrutivas, segredos ou publicação.
- Uma skill em Markdown **não requer pacotes para ser lida pelo Copilot**; o software final (treinamento e inferência do modelo) poderá exigir dependências próprias, a serem investigadas e justificadas pelos participantes.
- Não confundir **reconhecimento da skill** com **correção do resultado**. Testar em nova sessão e conferir alterações no repositório.

## Documentação oficial

- [Agent Skills no VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Agent Skills no GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
