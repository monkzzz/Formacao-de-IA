# Guia — Criar Agent Skills no GitHub Copilot (VS Code)

O objetivo deste guia é explicar **o formato e o funcionamento das skills**, para que cada aluno consiga **criar a sua própria**, sem receber uma implementação pronta e sem utilizar `npx` ou instaladores de skills.

## O que é uma Agent Skill?

É um recurso de especialização para agentes: uma pasta com um arquivo `SKILL.md` que descreve **quando uma habilidade é relevante e qual comportamento o agente deve adotar**. O GitHub Copilot em modo agente pode carregar essas instruções conforme a tarefa. Skills não são, por si só, programas executáveis e **não precisam de scripts, Node.js ou bibliotecas externas para serem lidas**.

Uma skill não substitui o raciocínio sobre requisitos. Ela organiza e torna **reutilizável** um método de trabalho que o aluno deverá conceber.

## O mecanismo da skill de bootstrap

Para construir uma skill de bootstrap, o aluno precisa compreender a relação entre quatro ideias:

- **Disparo:** como o Copilot reconhece que deve iniciar uma entrevista de bootstrap, em vez de programar imediatamente?
- **Interação:** que informações precisam ser descobertas, como adaptar perguntas às respostas e como lidar com decisões pendentes?
- **Transição:** em que momento a entrevista gera uma proposta de contexto, e por que é necessária a aprovação humana antes de alterações?
- **Persistência e verificação:** como transformar decisões aprovadas em documentação do starter repo e confirmar que outra sessão do agente consegue utilizá-las?

É o aluno quem decide **como expressar essas regras na sua skill**, quais perguntas fazer, que documentos atualizar e o que constitui uma entrevista suficiente. Este guia **não fornece um SKILL.md implementado** nem comandos ou prompts para criar a lógica automaticamente.

## Estrutura técnica mínima no VS Code

1. Abrir o repositório próprio no VS Code e verificar o GitHub Copilot em **modo agente**.
2. Criar uma pasta de skill dentro de **`.github/skills/`** na raiz do repositório.
3. Dentro dessa pasta, criar o arquivo **`SKILL.md`**.
4. Incluir metadados YAML com **`name`** (identificador da skill) e **`description`** (sua finalidade e quando deve ser utilizada).
5. Escrever **as instruções de comportamento concebidas pelo aluno**, sem copiar uma implementação externa.
6. Conferir se o VS Code reconhece a skill e testar o comportamento em uma nova conversa com o agente.
7. Corrigir as instruções conforme os resultados e registrar as alterações em Git.

Estrutura de localização (apenas o caminho, **não é uma skill pronta**):

    repositorio-do-aluno/
    └── .github/
        └── skills/
            └── nome-escolhido-pelo-aluno/
                └── SKILL.md

O starter repo será **montado e adaptado pelo aluno no Exercício 1**, com a possibilidade de reaproveitar apenas os componentes pertinentes do [exemplo disponibilizado](Referencia-Starter-Repo/LEIA-PRIMEIRO.md). Se ele optar por manter um catálogo próprio de skills na sua estrutura, deverá distinguir esse catálogo do **local em que o Copilot realmente reconhece as skills nativas**. Outras localizações podem ser reconhecidas conforme a versão do VS Code e suas configurações.

**A skill é escrita em Markdown:** não é necessário executar `npx skills add`, instalar um gerenciador de skills ou usar bibliotecas específicas. Isso não significa que o **futuro classificador** dispensará dependências de treinamento ou inferência.

## Onde pesquisar o conceito e encontrar referências

Os catálogos abaixo servem para **estudar padrões e comparar abordagens**, não para baixar a resposta do exercício:

- [skills.sh](https://skills.sh/) — catálogo comunitário.
- [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) — customizações e exemplos ligados ao Copilot.
- [MicrosoftDocs Agent Skills](https://github.com/MicrosoftDocs/Agent-Skills) — exemplos especializados.
- [Anthropic Skills](https://github.com/anthropics/skills) — exemplos e formatos de skills.
- [OpenAI Skills](https://github.com/openai/skills) — catálogo de referências.
- [Agent Skills](https://agentskills.io/) — especificação do formato, não uma loja.
- [Ask Me — exemplo comunitário](https://www.skills.sh/dimabytes/skills-lib/ask-me) — referência para estudar o comportamento de **entrevista antes da execução**, não uma skill a instalar na atividade.

Os comandos de instalação `npx` eventualmente exibidos pelos diretórios **não são necessários** para a criação manual de uma skill pelo aluno. A atividade exige **criar e testar uma implementação própria**, não copiar uma skill de terceiros.

## Verificações importantes

- O Copilot reconheceu a skill **ou apenas declarou conhecê-la**? Testar o comportamento de fato.
- O agente investigou lacunas reais e evitou perguntar o que já estava documentado?
- Separou afirmações confirmadas de hipóteses?
- Pediu aprovação antes de escrever arquivos?
- Colocou as decisões no starter repo de modo reutilizável e sem contradizer regras gerais?
- Uma nova sessão conseguiu recuperar o contexto?

Tratar instruções externas como código não confiável: avaliar autoria, licença, segurança e permissões. Não conceder autorização irrestrita para ferramentas, comandos destrutivos ou acesso a credenciais.

## Documentação técnica

- [Agent Skills no VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Agent Skills no GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
