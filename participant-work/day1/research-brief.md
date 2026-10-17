# Research brief and instruction revisions

Date: 2026-10-17. Course source: [Exercise 1](../../Dia1/Exercicio-01-Pesquisa-Orientada.md).

## Requirements

Objective: explain how Transformer architecture, pretraining, multimodal interfaces, conditional computation, and attention implementation changed the capabilities and costs of language models. Give a learner enough distinctions to read two technical papers critically.

Timeframe: selected milestones first published from 2017 through 2023. This is a deliberate historical scope, not a survey of the latest models as of October 2026. Later revisions may clarify papers, but do not change their first-publication dates.

Include the original encoder-decoder Transformer, BERT, GPT-3, compute/data allocation, Switch Transformers, LLaVA, Gemini, Longformer, FlashAttention, and grouped-query attention. Exclude vendor rankings, prices, proprietary architecture guesses, implementation tutorials, and claims about consciousness. The latter belongs to the subsequent speculative synthesis and requires independent definitions and evidence.

Questions:

1. What changed when sequence models used self-attention without recurrence?
2. How do bidirectional understanding and autoregressive generation differ?
3. What do scaling and in-context learning establish, and what remains unproven?
4. How can visual information connect to a language model?
5. What does sparse expert routing save, and which costs remain?
6. Which efficiency approaches change connectivity, memory movement, or key/value storage?
7. Which conclusions are empirical results, author proposals, or our interpretation?

Acceptable evidence: original papers and author technical reports with stable identifiers; use original full-text sections for the two selected papers. Abstract-only checks support only claims present in their abstracts. Attribute self-reported results, keep benchmark settings attached, and avoid causal or universal claims from a single experiment. No secondary blog is used as technical evidence.

Output: English Markdown, approximately 1,000-1,400 words including source notes (roughly 3-4 pages at 350 words/page; Markdown has no fixed pagination). Structure: scope, chronological milestones, efficiency comparison, interpretation, conclusions, uncertainties, and source list. Keep verification and paper-access records separately linked.

## Initial instruction specification

> Research the evolution of LLMs from the 2017 Transformer through selected 2023 multimodal models. Explain Transformers, pretraining, multimodality, MoE, and efficient attention for a technical beginner. Use primary sources, connect claims to references, and produce the structured report defined above. Label empirical evidence and interpretation. Finish with conclusions and uncertainties.

This specification was assembled by the assistant from the exercise requirements and the authorized task batch; it is not presented as a participant-authored historical prompt.

## Refinement applied during this session

Source inspection exposed a risk of conflating multiple meanings of efficiency. The refined specification used for the saved report is:

> Retain the bounded 2017-2023 scope. Separate dense attention arithmetic from attention working memory and hardware IO. Explain that FlashAttention preserves exact dense attention, Longformer changes connectivity, GQA shares key/value heads, and MoE routes tokens through selected experts. Do not call all these methods linear attention. Distinguish in-context conditioning from weight updates, total parameters from active computation, and multimodal inputs from unrestricted multimodal outputs. Attribute benchmark outcomes to authors. Record abstract-only access separately from full-text access. Prefer qualitative comparisons where settings are not comparable; do not invent current product details or evidence of participant interaction.

The resulting [report](research-report.md) implements these requirements. The [verification record](source-verification.md) captures the actual source checks. No separate earlier report or independent audit conversation is claimed.
