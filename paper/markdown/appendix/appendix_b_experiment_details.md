# Extended Experimental Results

This appendix provides the full per-iteration training progression, detailed speech-level score
tables, and the diagnostic analysis of the Group C regression that motivated the attention-only LoRA
fix (Appendix [ref:app:grpo_groups]).

## Five-Phase Training Roadmap

| **Phase** | **Name**          | **Focus**                                                     | **Status** |
|:---------:|:------------------|:--------------------------------------------------------------|:----------:|
|     1     | Iterative ORPO    | Core debate tactics, argument construction, all IPDA speeches |            |
|     2     | Research Skills   | Evidence curation, sentence selection, card cutting           |            |
|     3     | Cross-Examination | CX-specific tactics, GRPO training on dialogue                |            |
|     4     | Judge Adaptation  | Audience framing, bias-aware persuasion                       |            |
|     5     | Integration       | Consolidate phases 2–4 into unified system                    |  Planned   |

Five-phase training roadmap.

## Full Phase 1 Results (12 Iterations)

| **Iter** | **Mean**  | **Best** | **Zero%** | **Pairs** | **Args** | **Cost** |
|:---------|:---------:|:--------:|:---------:|:---------:|:--------:|:--------:|
| 1        |   0.198   |   0.85   |   18.2%   |    644    |    –     |   \$4    |
| 2        |   0.217   |   0.90   |   16.1%   |    638    |    –     |   \$4    |
| 3        |   0.245   |   0.88   |   15.3%   |    651    |    –     |   \$4    |
| 4        |   0.258   |   0.92   |   14.8%   |    627    |    –     |   \$4    |
| 5        |   0.270   |   0.89   |   14.5%   |    612    |    –     |   \$4    |
| 6        |   0.295   |   0.91   |   14.2%   |    64     |   639    |   \$4    |
| 7        |   0.286   |   0.88   |   14.0%   |    61     |   849    |   \$4    |
| 8        | **0.303** |   0.93   |   13.8%   |    66     |   1054   |   \$4    |
| 9        |   0.291   |   0.90   |   13.9%   |    63     |   1273   |   \$4    |
| 10       |   0.296   |   0.91   |   14.3%   |    63     |   1473   |   \$4    |
| 11       |   0.289   |   0.90   |   14.1%   |    71     |   2100   |   \$4    |
| 12       |   0.285   |   0.89   |   13.5%   |    228    |   2600   |   \$4    |

Full Phase 1 training progression across 12 iterations.

## Per-Speech-Type Progression

| **Speech Type** | **Iter 1–5** | **Iter 6–8** | **Iter 9–12** |
|:----------------|:------------:|:------------:|:-------------:|
| AC              |  0.65–0.75   |  0.78–0.85   |   0.83–0.90   |
| NC              |  0.65–0.75   |  0.78–0.85   |   0.85–0.90   |
| 1AR             |  0.55–0.70   |  0.70–0.80   |   0.75–0.85   |
| 1NR             |  0.55–0.70   |  0.70–0.80   |   0.85–0.90   |
| 2AR             |  0.55–0.70   |  0.70–0.80   |   0.75–0.88   |
| 2NR             |  0.55–0.70   |  0.78–0.85   | **0.85–0.95** |
| CX1/CX2         |  0.40–0.50   |  0.40–0.50   |   0.40–0.50   |

Per-speech score ranges. 2NR shows strongest improvement; CX remains flat.

## Full Tactic Performance (Iteration 12)

| **Tactic**                    | **Success Rate** | **Avg Reward** |
|:------------------------------|:----------------:|:--------------:|
| Dropped Argument Devastation  |       100%       |   0.80–0.90    |
| Depth Over Breadth            |       100%       |   0.63–0.90    |
| Strategic Concession Sequence |       100%       |   0.80–0.87    |
| Strategic Kick                |       100%       |   0.80–0.90    |
| Time Trap                     |       89%        |      0.77      |
| *Overall (all tactics)*       |       38%        |      0.62      |

Full tactic success rates (success = score $\geq 6$ AND on winning side).

## Phase 2: Sentence Selection Details

Training used the Phase 1 iteration 12 merged model as base:

- Round 1 (SFT): 3,000 examples with noise augmentation (variable-length outputs 50–150%)

- Round 2 (ORPO): 507 format-consistent pairs (481 F1-based + 26 rubric-based)

- LR: 5e-7 (reduced from 1e-6 to prevent overfitting)

Key technical discoveries: (1) positional bias in initial SFT (fixed patterns like \[4, 7, 12\]);
(2) format mismatch in preference pairs (terse chosen vs. verbose rejected); (3) overfitting at
LR=1e-6.

## Phase 3: Full CX Evaluation

End-to-end evaluation on 3 complete debates:

| **Metric**           | **Trained** | **Base** | **Delta** |
|:---------------------|:-----------:|:--------:|:---------:|
| Overall Score (0–10) |    3.74     |   3.46   |   +0.29   |
| Speech Score         |    3.35     |   3.08   |   +0.27   |
| CX Score             |    4.66     |   4.33   |   +0.33   |
| Avg Words/Debate     |    3,920    |  3,418   |   +502    |

Full debate comparison after CX training.

## Phase 4: Judge Adaptation Cross-Evaluation

| **Speech**    | **Econ Judge** | **Enviro Judge** | **Principled** |
|:--------------|:--------------:|:----------------:|:--------------:|
| Economic      |    **9.0**     |       2.0        |      1.8       |
| Environmental |      1.8       |     **9.0**      |      2.2       |
| Principled    |      3.0       |       9.0        |    **9.2**     |

Judge bias adaptation cross-evaluation. Diagonal dominance indicates genuine rhetorical adaptation.

## Iteration 3: GRPO Regression and Recovery

Sequential GRPO training on CX data (Group C) caused catastrophic regression: speech lengths
degraded by 75% (AC: 407 $\rightarrow$ 105 words). Root causes: overly aggressive LoRA (all 7
modules, 3.37B params), wide epsilon (0.3), data quality issues (one 367K-char degenerate response),
and logprob mismatch.

Fix: conservative GRPO with $\varepsilon = 0.15$, LR $= 1\text{e-}5$, attention-only LoRA (53M
params), strict data filtering (4,663 $\rightarrow$ 3,274 samples). Retrained model achieved 72.3%
accuracy with no regression.

**Key lesson:** For MoE architectures with offline GRPO, attention-only LoRA with tight epsilon
prevents catastrophic divergence from stale logprobs.
