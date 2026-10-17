# From Transformers to multimodal language models

This report follows selected developments from 2017 to 2023: how Transformers work, how training changed their uses, and how researchers tackled images, model size and memory costs. It was prepared with the current assistant on 2026-10-17 under the [research brief](research-brief.md), then revised following the [participant’s review](participant-review.md). Paper results are attributed to their authors; we have not reproduced the experiments.

A useful way to read this history is to ask what each change lets a model do, and what it costs. Translating a sentence, completing a paragraph and describing a photograph are different tasks. A larger model or a faster attention implementation does not improve all of them automatically.

## Architecture and pretraining

**2017:** Vaswani and colleagues proposed an encoder-decoder Transformer using attention and feed-forward layers without recurrent sequence processing. Queries and keys determine weights applied to values; multiple heads learn different projections. Positional information supplies order. Decoder masking prevents access to future output tokens during training. The paper's principal evaluation concerns machine translation, with additional parsing experiments; it does not establish general chatbot capability. Dense self-attention connects all positions, with per-layer complexity O(n²d) for sequence length n and representation dimension d. Parallel training over positions does not eliminate the sequential dependency of autoregressive generation. [S1, §§3-4](https://arxiv.org/html/1706.03762v7)

**2018:** BERT pretrains bidirectional representations using context from both sides and then fine-tunes for downstream tasks. This illustrates how a Transformer can support language understanding through pretraining rather than being limited to the original translation setup. Its abstract reports improvements on eleven NLP tasks. Those results concern the evaluated tasks and fine-tuning procedure; bidirectional representation learning is different from a causal next-token generator. [S2, abstract](https://arxiv.org/abs/1810.04805)

**2020:** GPT-3 investigates a 175-billion-parameter autoregressive model and evaluates task performance with examples and instructions supplied in context, without gradient updates for those evaluations. The authors report strong results on some tasks and difficulties on others, alongside concerns about misuse and dataset issues. In-context learning conditions predictions on a prompt; it should not be described as permanent retraining of model weights. [S3, abstract](https://arxiv.org/abs/2005.14165)

**2022:** The Chinchilla study examines parameter count and training-token allocation under a fixed compute budget. Its authors conclude that many large models in their comparison were undertrained and report benefits from allocating more tokens to a smaller model. This qualifies a narrative in which parameter count alone explains progress: training data allocation is another experimental variable. The conclusion is tied to the study's scaling experiments, not a universal recipe for every dataset or deployment. [S4, abstract](https://arxiv.org/abs/2203.15556)

### A practical comparison: reading a gap and writing a continuation

Consider two tasks with the same short sentence:

- **Fill a gap:** “The cat sat on the [MASK].” A bidirectional model such as BERT can use words on either side of a hidden token. Its training objective fits learning representations from surrounding context.
- **Continue a sentence:** “The cat sat on the …” An autoregressive model such as GPT-3 predicts a continuation from the preceding context. It cannot consult words that have not been generated yet.

These are teaching examples, not measured model outputs. They help explain why the training objective matters when comparing models. Neither example establishes which model is better at every language task.

Suppose you then put two examples of the desired answer format into a prompt. That changes the context for the next response. It does not, by itself, update the model’s weights. Fine-tuning involves parameter updates; giving examples in a prompt is a different operation. [S2, abstract](https://arxiv.org/abs/1810.04805), [S3, abstract](https://arxiv.org/abs/2005.14165)

## Sparse computation and multimodality

**2021:** Switch Transformers uses sparse expert routing to increase model capacity while controlling computation. A routing mechanism selects an expert rather than applying every expert to every token. The paper studies simplification, stability, and distributed training. Its large total parameter counts should not be read as the per-token cost of a dense model of the same size. The abstract also identifies communication and instability as practical difficulties for sparse expert approaches. [S5, abstract](https://arxiv.org/abs/2101.03961)

MoE is a choice about conditional computation. It does not by itself specify the modalities a model accepts or solve long-context attention. Expert storage, routing, hardware placement, and token distribution still matter when judging operational cost. A useful comparison must identify which cost is measured before calling one system more efficient.

**2023:** Visual Instruction Tuning introduces LLaVA by connecting a vision encoder with a language model and using generated multimodal instruction-following data. It demonstrates a route from language modeling to visual conversation through training an interface and instruction behavior. The authors' results support their evaluated setting; they do not establish reliable visual reasoning across arbitrary images or domains. [S6, abstract](https://arxiv.org/abs/2304.08485)

**2023:** The Gemini technical report describes a family trained for multimodal capabilities involving image, audio, video, and text, and reports evaluations across numerous benchmarks. This is an author technical report rather than independent certification of a deployed product. Modality support in a model family does not establish that every interface exposes every input or output modality. [S7, abstract](https://arxiv.org/abs/2312.11805)

Multimodality extends what information can condition model behavior. It should be assessed through modality-specific tasks, grounding, and failure cases. Neither fluent visual descriptions nor text benchmark performance alone establish dependable perception. The selected papers illustrate different routes to multimodality; they are not controlled comparisons of a single architecture variable.

### What changes when the input is a photograph?

Imagine asking, “What is on this table?” and attaching a photograph. LLaVA illustrates how a vision encoder can supply image information to a language model. The model’s answer can then depend on the image as well as the question. That connection is the architectural idea; whether it correctly identifies a small or partly hidden object needs a separate test. [S6, abstract](https://arxiv.org/abs/2304.08485)

MoE addresses another problem: how to use a large collection of parameters while activating only selected experts for each token. It does not itself provide the visual input path. A model can combine these choices, but “multimodal” and “mixture of experts” describe different features. [S5, abstract](https://arxiv.org/abs/2101.03961)

## Efficiency as context grows

Several techniques address different bottlenecks:

| Approach | Supported mechanism | What the claim does not establish |
| --- | --- | --- |
| Longformer | Local-window and global attention; linear scaling with sequence length for its configured attention pattern. [S8, abstract](https://arxiv.org/abs/2004.05150) | Identical connectivity to unrestricted dense attention. |
| FlashAttention | Tiling and recomputation reduce high-bandwidth-memory traffic while computing exact attention. [S9, §§3.1-3.2](https://arxiv.org/html/2205.14135v1) | Linear arithmetic for exact dense attention. |
| Grouped-query attention | Shares key/value heads among groups of query heads, between multi-head and multi-query attention. [S10, abstract](https://arxiv.org/abs/2305.13245) | Removal of all token-to-token interactions or all inference costs. |

FlashAttention's Theorem 1 retains O(N²d) arithmetic and uses O(N) additional memory beyond inputs and output under its stated setup. Its limitation discussion identifies kernel engineering and portability across GPU architectures. Exactness describes the attention computation, allowing normal numerical differences; it does not promise identical application outputs under every implementation. [S9, §3.1 and §5](https://arxiv.org/html/2205.14135v1)

These techniques can be complementary because connectivity, memory movement, and key/value sharing are different design dimensions. Faster kernels do not prove better reasoning over long documents. A context window's capacity and effective use of distant information require separate evaluation. End-to-end latency also depends on workloads and the rest of the model, so isolated improvements should not be multiplied into an unsupported total speedup.

### Which efficiency change would help with a long document?

Suppose you want a model to process a longer document. Before choosing a method, ask where the cost comes from:

| Your question | Relevant approach | Tradeoff or boundary |
| --- | --- | --- |
| Can we restrict which positions attend to one another? | Longformer uses local windows and selected global connections. | This changes the attention pattern. |
| Can we execute dense attention with less memory traffic? | FlashAttention reorganizes the calculation into blocks. | Dense arithmetic remains quadratic; hardware and workload affect speed. |
| Can query heads share key/value heads? | GQA groups query heads around shared keys and values. | Sharing these heads does not remove all other inference costs. |
| Can we activate fewer experts per token? | MoE routes a token to selected experts. | Expert storage and routing still have costs. |

This is a comparison of mechanisms from the sources above, not a benchmark ranking. There is no single “most efficient” choice without specifying the model, hardware, workload and measurement. A system may use several of these methods together.

## Conclusions and unresolved questions

The evidence supports a history of interacting changes: attention-based architecture, pretraining objectives, data/compute allocation, sparse capacity, multimodal training, and hardware-aware execution. It does not support a single ladder where each later paper supersedes every earlier method. The appropriate question is which measured capability or cost each intervention changes.

Important uncertainties remain. Comparisons span different data, compute budgets, tasks, and publication settings. Most supporting papers were checked at abstract level here; only the two selected full texts received section-level inspection. No experiments were reproduced. This bounded review omits many milestones and all post-2023 developments. It provides no evidence about consciousness, calibrated correctness probabilities, or current commercial model internals.

For the next exercise, read S1 and S9 together: one defines the attention architecture and its complexity, while the other studies how to execute that computation with less memory traffic. The [selection record](paper-selection.md) preserves access details; the [verification ledger](source-verification.md) distinguishes checked statements from interpretation and remaining work.

## Source identities

All links above were opened on 2026-10-17. Identifiers preserve traceability even if web rendering changes.

- S1: Vaswani et al., *Attention Is All You Need* (2017), arXiv:1706.03762; inspected HTML v7.
- S2: Devlin et al., *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding* (2018), arXiv:1810.04805.
- S3: Brown et al., *Language Models are Few-Shot Learners* (2020), arXiv:2005.14165.
- S4: Hoffmann et al., *Training Compute-Optimal Large Language Models* (2022), arXiv:2203.15556.
- S5: Fedus et al., *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity* (2021), arXiv:2101.03961.
- S6: Liu et al., *Visual Instruction Tuning* (2023), arXiv:2304.08485.
- S7: Gemini Team et al., *Gemini: A Family of Highly Capable Multimodal Models* (2023), arXiv:2312.11805.
- S8: Beltagy et al., *Longformer: The Long-Document Transformer* (2020), arXiv:2004.05150.
- S9: Dao et al., *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness* (2022), arXiv:2205.14135; inspected HTML v1.
- S10: Ainslie et al., *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints* (2023), arXiv:2305.13245.
