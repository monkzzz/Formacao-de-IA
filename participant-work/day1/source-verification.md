# Source verification record

Date: 2026-10-17. Applies to the [saved report](research-report.md). This is the verification step within Exercise 1, not the separate fresh-conversation audit required by Exercise 4.

Primary-source pages were opened through the web tool. Full HTML documents for S1 and S9 were made available to the current assistant; focused section inspection supports the claims below. Other publications were checked through their arXiv abstracts. No reproduction, complete methodological review, or independent confirmation of author-reported benchmarks is claimed.

| Claim checked | Source and locator | Outcome and limit |
| --- | --- | --- |
| Transformer uses encoder/decoder attention, masking, and position information | [S1](https://arxiv.org/html/1706.03762v7), §§3.1-3.5 | Supported; model is not described as attention alone without feed-forward layers. |
| Dense self-attention has O(n²d) per-layer complexity | S1, §4, Table 1 | Supported with n and d defined; training parallelism is distinct from generation. |
| BERT uses bidirectional pretraining and downstream fine-tuning | [S2](https://arxiv.org/abs/1810.04805), abstract | Supported at abstract level. |
| GPT-3 evaluates few-shot conditioning without gradient updates | [S3](https://arxiv.org/abs/2005.14165), abstract | Supported; no claim of permanent learning from prompts. |
| Compute-optimal training involves both parameters and tokens | [S4](https://arxiv.org/abs/2203.15556), abstract | Supported; universal scaling law claim excluded. |
| Switch uses sparse expert computation | [S5](https://arxiv.org/abs/2101.03961), abstract | Supported; total parameters and active computation kept distinct. |
| LLaVA connects a visual encoder and language model using instruction tuning | [S6](https://arxiv.org/abs/2304.08485), abstract | Supported; no unrestricted perception reliability claim. |
| Gemini report describes multimodal model family | [S7](https://arxiv.org/abs/2312.11805), abstract | Supported as author report; interface availability not inferred. |
| Longformer combines local and global attention | [S8](https://arxiv.org/abs/2004.05150), abstract | Supported; sparse pattern distinguished from dense exactness. |
| FlashAttention changes IO and memory, retaining quadratic dense arithmetic | [S9](https://arxiv.org/html/2205.14135v1), §3.1 Theorem 1, §3.2 | Supported; linear additional memory is not linear FLOPs. |
| Kernel engineering and portability are limitations | S9, §5 | Supported for that paper's implementation; no current-library claim. |
| GQA shares key/value heads across query groups | [S10](https://arxiv.org/abs/2305.13245), abstract | Supported; no unverified throughput numbers included. |

Refinements made before saving: separated the efficiency mechanisms, bounded the chronology, labelled interpretations, omitted cross-paper benchmark rankings, and separated source support from experimental replication. These were applied as drafting constraints; no fabricated earlier draft is retained.

One inspected URL, arXiv:2301.11916, resolved to a paper about latent-variable explanations of in-context learning rather than a needed milestone. It was excluded from the report and source list. Source identities were checked against returned titles rather than assuming an identifier's content.

Remaining uncertainties: abstract checks do not validate dataset composition or numerical methodology; HTML equations/figures may differ from PDF presentation; no source establishes participant understanding or instructor acceptance. Later reading notes should inspect full text before extending abstract-supported claims.
