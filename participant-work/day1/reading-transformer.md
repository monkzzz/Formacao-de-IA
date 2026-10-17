# Reading note: Attention Is All You Need

Prepared 2026-10-17. Source S1: Vaswani et al. (2017), [versioned full text, v7](https://arxiv.org/html/1706.03762v7). Section identifiers below refer to that rendering. The [selection record](paper-selection.md) explains access limitations.

These progressively narrower questions were formulated and answered by the assistant in this session, then checked against the named sections. They are a learning artifact, not a transcript of participant questions or a claim of experimental replication. All source-based answers are paraphrases; no direct quotations are used.

| Stage / question | Grounded answer | Locator / status |
| --- | --- | --- |
| 1. What problem motivates the work? | Sequential recurrent computation constrains training parallelism. | §1; author motivation |
| 2. What is the main objective? | Replace recurrence with attention for sequence transduction. | §§1, 3; author proposal |
| 3. How does it work? | Encoder/decoder stacks combine multi-head attention, feed-forward layers, positional information, and causal decoder masking. | §§3.1-3.5; method paraphrase |
| 4. What data support the evaluation? | WMT 2014 English-German: approximately 4.5 million sentence pairs; English-French: 36 million. | §5.1; reported data |
| 5. What result is identifiable? | Transformer-big reports 28.4 BLEU on English-German newstest2014. | §6.1, Table 2; author result |
| 6. Which assumptions matter? | The scaling justification assumes independent, zero-mean, unit-variance query/key components. | §3.2.1 footnote; explanatory assumption |
| 7. What limit do the authors acknowledge? | Longer sequences motivate restricted attention as future work. | §4; acknowledged cost issue |
| 8. What should a reader question? | Table 2 gives English-French 41.8 BLEU, whereas nearby prose says 41.0. | §6.1; unresolved textual discrepancy |

## Interpretation and conclusion

My inference: a translation result cannot establish subjective experience. A separate bridge from the measured task to the proposed psychological property would be needed. This is a reasoning constraint imposed by this reading exercise, not an author conclusion.

The architecture makes a useful starting point for the [synthesis](synthesis-original.md), provided its task and evidence boundaries remain explicit. For further reading, ask how changing a component while holding training conditions fixed would affect results. Do not silently choose one English-French score; an author correction or authoritative source comparison would be needed to resolve the discrepancy.

Verification performed: inspected architecture §§3.1-3.3, complexity §4, data §5.1, and results §6.1. PDF page positions and experimental reproducibility were not verified. Remaining uncertainty concerns the reported English-French inconsistency and generalization beyond the studied settings.

## R02 follow-up: plain explanation and competing readings

Added 2026-10-17 by the assistant; this is not participant-authored dialogue.
Imagine each word asking which other words help describe it. Attention assigns
weights to their information and combines it. A decoder predicting the next word
must hide later answer words, or training would let it look at the answer. During
training many known positions can still be processed together; producing a new
translation remains sequential because each new word uses the words already
generated. This analogy omits vector projections and training details.

Passage examined: the masking/shift explanation in
[§3.1, Decoder, of v7](https://arxiv.org/html/1706.03762v7#S3.SS1), read again on 2026-10-17.

| Candidate reading | Assessment against the passage |
| --- | --- |
| Masking removes every kind of sequential dependence, including when generating a translation | Unsupported. §3 explicitly describes autoregressive output; parallel training positions do not make unknown future outputs available |
| Masking prevents access to future target positions while permitting parallel computation on known training inputs | Supported by the decoder's mask and one-position shift; distinguish training computation from generation |

The resolved distinction improves the architectural explanation; it does not
measure new performance or resolve the separate English–French BLEU discrepancy.

## R01 participant-directed example and diagram

Added in response to the participant’s request for both a worked sentence example and a diagram. The [review record](participant-review.md) preserves the actual answers. This is an assistant explanation, not a measured attention trace.

Take “The animal crossed the road because it was tired.” When building a representation of “it,” an attention head can combine information from earlier words, including “animal.” Different heads may use different relationships. These links are learned, and an attention weight alone does not prove a grammatical explanation or a reasoning step.

For a simplified numerical example, suppose three available value vectors are animal = (1, 0), road = (0, 1), tired = (1, 1), and their attention weights are 0.6, 0.1 and 0.3. The weighted result is 0.6(1, 0) + 0.1(0, 1) + 0.3(1, 1) = (0.9, 0.4). The vectors and weights are invented solely to show the calculation. A real layer obtains queries, keys and values through learned projections and computes weights using scaled dot products and softmax. A causal decoder includes only positions available at that prediction step.

```mermaid
flowchart LR
    A[Tokens and position information] --> B[Learned queries, keys and values]
    B --> C[Query-key scores and causal mask]
    C --> D[Softmax weights]
    D --> E[Weighted combination of values]
    B --> E
    E --> F[Head combination and output projection]
    F --> G[Residual connections, normalization and feed-forward processing]
    G --> H[Further layers and next-token scores]
```

The diagram simplifies a causal language model, rather than reproducing the original encoder-decoder architecture. Training on known sequences permits parallel position calculations with masking; generating an unknown continuation still requires successive token steps. This explanation uses the original note’s S1 §§3–4 source boundary.

### Connection to a current open model

The participant asked how these ideas translate to current LLM technology. As a concrete documented example, the [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B), inspected on 2026-10-17, identifies a causal language model with 32 query heads and eight key/value heads. Those grouped heads adapt the attention machinery introduced in the earlier reading. This is one available model example, not a claim about every current model or a claim that it is the newest release.

The useful connection is that later LLMs retain attention-based building blocks while changing architectural details and training. The original translation model is therefore a foundation to learn from, rather than an exact blueprint of every present-day assistant. The model card was inspected; no model was downloaded or executed.
