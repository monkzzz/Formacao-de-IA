# Reading note: FlashAttention

Prepared 2026-10-17. Source S9: Dao et al. (2022), *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*, [full text v1](https://arxiv.org/html/2205.14135v1). See the [selection record](paper-selection.md) for access limits.

The assistant formulated these questions, answered them progressively, and checked the cited sections during this session. Answers paraphrase the paper; no direct quotations or reproduced experiments are claimed.

| Stage / question | Grounded answer | Locator / status |
| --- | --- | --- |
| 1. What problem is addressed? | Materialized attention intermediates create costly GPU memory traffic. | §2.2; problem paraphrase |
| 2. What is the objective? | Execute exact attention with fewer HBM accesses. | §3; author objective |
| 3. Which method enables this? | Tiling, normalization statistics, and backward recomputation avoid storing full attention intermediates. | §3.1, Algorithm 1; method |
| 4. What evaluation data are named? | Wikipedia for BERT, OpenWebText for GPT-2, and Long-Range Arena tasks. | §4.1; reported data |
| 5. What concrete result is reported? | BERT-large reaches 72% masked-language-model accuracy in 17.4 ± 1.4 versus 20.0 ± 1.5 minutes: ten runs, eight A100s. | §4.1, Table 1; author result |
| 6. Which complexity assumptions apply? | The IO analysis constrains SRAM size M by d ≤ M ≤ Nd. | §3.2, Theorem 2; stated regime |
| 7. What does exactness leave unchanged? | Dense arithmetic remains O(N²d); additional memory is O(N), under the theorem's setup. | §3.1, Theorem 1 |
| 8. What limitations are acknowledged? | Kernel development requires substantial effort; portability across GPU architectures is uncertain. | §5; author limitations |

## Interpretation and conclusion

My inference: a cheaper execution path cannot by itself establish the psychological significance of the computed representations. An experiment would need to measure that proposed property directly or justify its indicators. The benchmark above measures a training outcome and elapsed time.

For the [synthesis](synthesis-original.md), treat an engineering improvement and a claim about experience as separate propositions. Ask which intervention changes the proposed cognitive mechanism, which only changes its implementation, and how a test would distinguish them.

Verification performed: checked §2.2, §§3.1-3.2, §4.1 Table 1, and §5. Numerical results remain author-reported. No kernels were run; no PDF pagination or cross-hardware reproduction was checked. Further reading should distinguish the dense algorithm from the paper's separately described sparse extension before comparing results.

## R02 follow-up: plain explanation and competing readings

Added 2026-10-17 by the assistant, not a participant interaction. Imagine doing
the same calculation with a small fast workbench and a large slow cupboard.
FlashAttention brings useful blocks to the workbench and combines partial results
carefully, avoiding a huge intermediate table in the cupboard. It can repeat
some arithmetic to save expensive trips. The analogy describes memory movement,
not a claim that all computation becomes linear or every device gets faster.

Passage examined: [v1 §3.1, Algorithm 1 and Theorem 1](https://arxiv.org/html/2205.14135v1#S3.SS1),
read again on 2026-10-17. Two candidate meanings of “exact” are:

| Candidate reading | Assessment against the passage |
| --- | --- |
| It approximates dense attention by skipping low-weight pairs | Unsupported for the dense algorithm in Theorem 1; the paper discusses a separate block-sparse extension |
| It evaluates the same mathematical dense-attention output using blocked execution and normalization statistics | Supported by the theorem; arithmetic remains quadratic in sequence length under its setup while additional storage and memory traffic are different quantities |

“Same mathematical output” does not guarantee bit-for-bit equality for every
floating-point implementation or hardware platform. This is an interpretation
boundary, not a new kernel experiment or a universal speed claim.
