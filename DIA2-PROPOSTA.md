# Dia 2 — Proposta de trabalho

## Estado e decisões pendentes

**Status update, 2026-10-17:** the following proposal is historical. The personal
fork now contains the [starter](participant-work/starter/README.md),
[bootstrap/context evidence](participant-work/day2/bootstrap-next-ten.md),
[real Issues](participant-work/day2/issue-register.md), trained classifier and
[v3.10.0 public application checks](participant-work/day2/submission-browser-delivery.md).
English, the chosen assistant and preservation of the current website are
confirmed preferences. The original planning text below is retained; it does not
describe current absence of those deliverables. GitHub Pages, original process
approval acceptance and actual teacher feedback remain pending. See [tasks](TASKS.md).

Este documento é uma proposta de preparação, não uma entrega concluída. O projeto pessoal ainda não foi criado. Confirmar com o participante:

1. Caminho do novo repositório e destino na sua conta GitHub.
2. Preferência de autonomia: aprovar cada plano ou delegar tarefas rotineiras e rever decisões importantes.
3. Idioma preferido para código, documentação e comunicação.

## Exercício 1 — Starter reutilizável

Estrutura proposta, independente de linguagem e do classificador:

```text
AGENTS.md                       regras sempre ativas e mapa de contexto
README.md                       utilização e início de um novo projeto
.github/copilot-instructions.md orientação de entrada para o Copilot
docs/contexto.md                requisitos confirmados, hipóteses e pendências
docs/decisoes.md                decisões, motivos e condições de revisão
docs/conhecimento.md            descobertas verificadas e como reproduzi-las
docs/capacidades.md             ferramentas necessárias e disponibilidade comprovada
docs/procedimentos/trabalho.md  investigar, planear, executar e validar
docs/procedimentos/git.md       preservar alterações, rever diff e versionar
docs/evidencias.md              verificações executadas e resultados
```

Criar apenas documentos com conteúdo útil; acrescentar outros quando necessários. O contexto inicial deverá declarar que o projeto ainda não foi definido. Nenhuma arquitetura, dataset ou skill de entrevista entra nesta etapa.

### Análise da referência

Fonte: `Dia2/Referencia-Starter-Repo/Starter-Repo/`.

| Componente | Proposta | Justificação |
| --- | --- | --- |
| Contrato principal e procedimentos separados | Adaptar | Manter instruções frequentes curtas e carregar detalhes conforme a tarefa |
| Procedimento de validação | Adaptar | Executar verificações pertinentes, conservar resultados e declarar lacunas |
| Procedimento Git | Adaptar | Rever estado e diff, selecionar arquivos explicitamente e preservar trabalho existente |
| Conhecimento, contexto e decisões | Simplificar | Separar requisitos, motivos de decisões e descobertas comprovadas sem índices redundantes |
| Catálogos CLI, MCP e skills | Consolidar inicialmente | Distinguir documentado, necessário e disponível sem instalar capacidades sem finalidade |
| Publicação npm/PyPI e regras pessoais do autor | Descartar inicialmente | Não são requisitos de um starter genérico |
| Commit e push automáticos | Decisão pendente | Devem refletir a preferência do participante |

Registar atribuição e verificar a licença antes de copiar texto. A referência foi analisada; esta proposta não copia a sua implementação integral.

### Verificação da etapa

- Nova sessão: recuperar regras, contexto e próxima tarefa sem consultar esta conversa.
- Reutilização: aplicar a estrutura a outro projeto hipotético sem pressupor ML ou uma stack.
- Autonomia: pedir uma revisão segura da documentação e observar investigação, alterações, verificação e respeito pelas preferências.
- Guardar evidências reais; estes ensaios ainda não foram executados.

## Exercícios seguintes e critérios de passagem

1. **Bootstrap:** pesquisar o padrão Ask Me; criar uma skill própria; testar perguntas adaptativas, distinção entre confirmação e hipótese, aprovação antes da escrita e recuperação noutra sessão.
2. **Planeamento:** discutir alternativas técnicas, aprovar a especificação e criar Issues reais no GitHub antes da implementação.
3. **Modelo:** usar MNIST original, separar treino/validação/teste, treinar efetivamente, conservar logs e pesos e verificar métricas e exportação.
4. **Aplicação:** desenho, upload múltiplo, pré-visualizações, pontuações, ativações reais, inferência no navegador e paridade com o modelo de origem; publicar no GitHub Pages.
5. **Desafio:** fixar versão e pesos; carregar os dez PNGs no site público; guardar previsões antes de consultar rótulos; comparar depois sem substituir o resultado inicial.
6. **Feedback:** professor testa o site; registar observações reais, Issues, correções e evidências antes/depois. A avaliação humana não pode ser substituída por um relatório inventado.

## Ambiente observado

Git e Python 3.12 estão disponíveis no PATH. `gh` e `node` não foram encontrados no PATH nesta verificação; isso não comprova ausência no computador. A autenticação GitHub e a capacidade de publicação ainda não foram verificadas. Nenhuma instalação foi feita.
