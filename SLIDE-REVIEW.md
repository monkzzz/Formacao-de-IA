# Slide Review and Course Questions

Review date: 2026-10-17. Scope: preparation for the course exercises, using the PDFs supplied in this checkout. Page numbers below are PDF page positions.

The joint GSS deck has selectable text; the other ten decks are image-only. Review used extracted GSS text and rendered contact sheets covering every page of the other decks. Contact sheets support topic review, not a complete transcription or independent validation of every small caption, benchmark, product claim, or reference. Rendering dependencies were installed temporarily outside project requirements; the slides were not changed.

## Day 1

| Deck | Pages | Review notes and exercise connection |
| --- | ---: | --- |
| [Whoami](Dia1/Teorico/Whoami.pdf) | 27 | Course introduction and artistic presentation conventions. Pages 19–27 explain the two-day theory/practice format and encourage questions. Use this to set expectations for the research and practical sessions. |
| [Joint GSS modules](Dia1/Teorico/20261012--forma%C3%A7%C3%A3o_gss_modulos_1.1_1.2-HCG-v_conjunta_dia1.pdf) | 83 | Pages 7–50 cover learning paradigms, forward passes, gradients, validation, metrics, and five vision tasks. Pages 52–82 connect tokens, embeddings, attention, generation, adaptation, context, and multimodality to the twelve GSS demonstrations. UCI 8×8 examples are distinct from Day 2 MNIST. |
| [The Basics](Dia1/Teorico/The%20Basics.pdf) | 48 | Models, inference, hallucination, sycophancy, agents/harnesses, tools, Markdown, skills, and context. Pages 37–48 emphasize clear requests and coherent context. Apply to all four research exercises and the later starter design. |
| [LLM Anatomy](Dia1/Teorico/LLM%20Anatomy.pdf) | 83 | Prompt specificity, language/persona claims, revision and cross-checking, system/user messages, tool outputs, context limits, compaction, latency, and appropriate task boundaries. Pages 39–46 support the separate audit/revision conversations; pages 73–82 motivate tool verification and explicit limitations. |
| [From LLM to Chatbot](Dia1/Teorico/From%20LLM%20to%20Chatbot.pdf) | 33 | Contrasts traditional NLP pipelines with LLM-based applications; discusses agents, summarization, structured use cases, and evaluation. Pages 25–26 emphasize trying, testing, and evaluating use cases. Relevant to report synthesis and planning an actual application rather than treating fluent output as proof. |
| [Context Eng](Dia1/Teorico/Context%20Eng.pdf) | 49 | Pages 5–17 show how missing requirements undermine an apparently reasonable report. Later pages discuss task-dependent relevance, layered context, `AGENTS.md`, supporting documents, on-demand loading, and maintenance. Connect to research requirements and the reusable starter/bootstrap exercises. |
| [Model Chosing](Dia1/Teorico/Model%20Chosing.pdf) | 19 | Task-specific evaluation, benchmark methodology, quality/cost/latency tradeoffs, and domain-specific scoring. Relevant to research source selection and comparing technical options. Benchmark rankings and numerical product claims are historical slide content, not current recommendations verified by this review. |

## Day 2

| Deck | Pages | Review notes and exercise connection |
| --- | ---: | --- |
| [Coding Agents](Dia2/Teorico/Coding%20Agents.pdf) | 38 | Agent loops, tool observations, limits of long tasks, smaller bounded assignments, and the distinction between model, agent, and harness. Pages 24–31 emphasize completed tasks, clear requirements, and meaningful verification. Supports Exercise 3's task decomposition and implementation cycle. |
| [Agentic Context Eng](Dia2/Teorico/Agentic%20Context%20Eng.pdf) | 44 | Repository familiarization, bootstrap questions, persistent instructions, useful folder semantics, reusable knowledge, context cleanup, and Git checkpoints. Pages 37–42 connect starter reuse, interview-driven context, and ongoing maintenance. Direct preparation for Exercises 1 and 2. |
| [Task eng](Dia2/Teorico/Task%20eng.pdf) | 34 | Objectives, scope, constraints, acceptance criteria, Issues/specifications, planning, proof in PRs, dependencies, and context handovers. Pages 7–17 connect requirements to verifiable outcomes; pages 31–33 emphasize keeping persistent context synchronized. Supports planning before implementation and traceable corrections. |
| [VDD and Autonomy](Dia2/Teorico/VDD%20and%20Autonomy.pdf) | 21 | Verification-driven development, checkpoints, test strategy, review, and bounded autonomy. Pages 10–14 emphasize human-defined acceptance checks and review evidence. Supports model/browser parity checks, publication validation, and the feedback/correction loop. |

## Takeaways for the exercises

1. Research work needs an explicit question, scope, source standard, output format, and uncertainty record. A second model response is a review aid; original sources still need checking.
2. Training changes parameters; inference and prompting usually use fixed parameters. The didactic attention values and recorded LLM examples must be identified accurately when discussing the demonstrations.
3. Validation selects checkpoints and development choices. The held-out MNIST test and official challenge must remain outside tuning. A high softmax score does not establish correctness.
4. Persistent context should separate generic working rules, project decisions, reusable knowledge, and execution evidence. Context should be sufficient for a later session to identify the next task.
5. Define observable acceptance criteria before asking an agent to implement. Use actual commands, metrics, UI behavior, and model identities to assess completion.
6. Later challenge runs remain later iterations. Preserve original predictions and record the exact release used for subsequent deployment verification.

## Questions to resolve during the course

| Question | Relevant lesson | Why it remains open |
| --- | --- | --- |
| Will the instructor accept the participant's explicit decision to use this assistant instead of Copilot, including an equivalent interview skill workflow? | All practical work; especially Day 2 Exercise 2 | The participant has decided against Copilot; course assessment acceptance has not been recorded. |
| Is a personal fork containing `dia2-local/` acceptable, or must the classifier be extracted into a standalone participant repository? | Day 2 Exercises 1 and 3 | Existing history should be preserved rather than presenting a reconstruction as the original sequence. |
| Must the final submission use GitHub Pages, or can the existing HTTPS host be accepted? | Day 2 Exercise 3, Part 3 | A Pages destination is prepared, but the hosting substitution requires instructor acceptance if retained. |
| How should missing original pre-implementation Issue approvals be assessed for the existing implementation? | Day 2 Exercise 3, Part 1 | Retrospective documentation cannot establish earlier approval. |
| Which original papers and definitions should bound the speculative consciousness discussion? | Day 1 Exercises 1–3 | Source selection and an operational definition are still part of the participant's research work. |
| Which claims about personas, language, and benchmark scores require primary-source checking before reuse? | LLM Anatomy and Model Chosing | This slide review did not independently verify empirical claims. |
| What is the minimum network visualization evidence the teacher expects, and which release should be assessed? | Day 2 Exercise 3 and feedback | Existing activation evidence needs to be tied to the submitted release and teacher review. |

## Observed teaching-material issues

- The joint GSS slides use shorter original script names such as `05_mlp_digitos.py`. In this repository, use the full `dia1_modulo1_05_mlp_digitos.py` names and the commands in the [GSS guide](Dia1/Exercicios-GSS/README.md).
- The image-only format makes search and accessible text extraction difficult. Searchable transcripts would improve reuse, but creating them is outside this preparation batch.
- Some decks include production screenshots or presentation-development material. For example, From LLM to Chatbot pages 27–32 contain image-generation conversation screenshots; LLM Anatomy page 18 renders as a solid-colored slide. Record these as review observations rather than changing the original PDFs during preparation.

Review completion means that the supplied materials have been inspected and mapped to the exercises. It does not certify participant attendance, source verification, or exercise completion.
