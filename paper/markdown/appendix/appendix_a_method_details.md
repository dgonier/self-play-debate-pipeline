# Extended Method Details

This appendix documents the implementation details of the training pipeline referenced in
Section [ref:sec:method]:
model configuration, the epsilon-greedy tactic exploration policy, the full research pipeline used
for evidence curation, and the evidence verification rubric.

## Model Configuration

<div id="tab:model_config">

| **Parameter**        | **Value**                                          |
|:---------------------|:---------------------------------------------------|
| Base model           | Qwen3-30B-A3B-Thinking (MoE: 30B total, 3B active) |
| LoRA rank            | 32, $\alpha$=64, targets: q/k/v/o projections      |
| LoRA dropout         | 0.05                                               |
| ORPO $\beta$         | 0.1                                                |
| Learning rate        | $5 \times 10^{-7}$                                 |
| Epochs per iteration | 2                                                  |
| DeepSpeed            | ZeRO-3 across 8 GPUs                               |
| Inference            | vLLM with tensor parallelism                       |

Training configuration for Phase 1 iterative ORPO.

</div>

## Epsilon-Greedy Tactic Exploration

The tactical playbook uses a 3-tier hierarchy:

- **AtomicActions** ($\sim$<!-- -->21K): Single debate moves (77 ActionTypes $\times$ 39 TargetTypes
  $\times$ 7 PrivateIntents)

- **MicroTactics** ($\sim$<!-- -->10$^9$): 2–4 move sequences, the GRPO optimization unit

- **MacroTactics** (25+): Named strategies with game-theoretic payoff matrices

Sampling uses epsilon-greedy: $\sim$<!-- -->70% exploit (proven tactics), $\sim$<!-- -->25% explore
(novel combinations), $\sim$<!-- -->5% innovate (random). Tactics are promoted to the permanent
playbook when uses $\geq 5$ and avg_reward $\geq 0.6$. Epsilon grows dynamically with playbook size:
$\varepsilon = \min(0.9, \varepsilon_{\text{base}} + 0.003 \times \lfloor|\text{book}|/10\rfloor)$.

Speech-type-specific epsilon values: AC/NC (constructive) $\varepsilon = 0.6$–$0.7$; 1AR/NR
(rebuttal) $\varepsilon = 0.4$; 2AR (final) $\varepsilon = 0.3$.

## Research Pipeline

Evidence retrieval uses a consolidated pipeline:

1.  **LLM**: Generate search queries from debate context

2.  **Automated**: Search $\rightarrow$ clean (regex) $\rightarrow$ chunk (sentence-level)
    $\rightarrow$ score ($0.7 \times$ embedding $+ 0.3 \times$ BM25) $\rightarrow$ window expansion
    ($\pm$<!-- -->3 sentences)

3.  **LLM**: Select sentences by ID and format evidence cards

This reduces the original 9-LLM-call pipeline to 2–3 calls per research hop ($\sim$\$0.05/hop,
10–15s latency).

## Evidence Verification Scoring

Evidence quality uses a 6-level scale with asymmetric GRPO penalties:

| **Category**  |   **Score**    | **GRPO Weight** |
|:--------------|:--------------:|:---------------:|
| EXACT_MATCH   |      +1.0      |   1.0$\times$   |
| PARAPHRASE    |      +0.7      |   1.0$\times$   |
| WEAK_SUPPORT  |      +0.3      |   1.0$\times$   |
| MISQUOTE      | $-$<!-- -->0.5 |   1.5$\times$   |
| FABRICATION   | $-$<!-- -->0.8 |   2.0$\times$   |
| HALLUCINATION | $-$<!-- -->1.0 |   2.0$\times$   |

Evidence verification categories with asymmetric penalties.

## Design Rationale

**ORPO over DPO:** Iterative training requires no frozen reference model. DPO would require careful
reference model scheduling across iterations.

**Trajectory-level evaluation:** Debate quality emerges from cumulative choices across speeches.
Scoring complete debates captures strategic dynamics that per-turn evaluation misses.

**Sentence-ID selection over RAG:** Hard constraint prevents fabrication—invalid IDs fail at
generation time, valid IDs guarantee verbatim text.
