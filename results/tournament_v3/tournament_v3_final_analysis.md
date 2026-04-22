# Tournament V3: Final Statistical Analysis

**Generated**: 2026-02-19 14:54 UTC
**Trained Model**: `dgonier/ipda-iter3-grpo-final` (Qwen3-30B-A3B, SFT + GRPO)
**Base Model**: `Qwen/Qwen3-30B-A3B-Thinking-2507` (raw, untrained)

---

## Pipeline Judge Results

**N** = 23 complete debates (1 incomplete, excluded)

| Metric | Value |
|--------|-------|
| Trained wins | 7 / 23 (30%) |
| Base wins | 16 / 23 (70%) |
| Mean score diff | -2.1 (SD=16.9) |
| Median score diff | -6.0 |
| Binomial p-value | 0.0931  |
| Paired t-test p | 0.5512  |
| Cohen's d | -0.126 (negligible) |
| Significant (p<0.05)? | **NO** |
| Debates needed (power=0.80) | 493 |

### Side Bias

| Side | N | Trained Wins | Win Rate |
|------|---|-------------|----------|
| Trained as AFF | 12 | 1 | 8% |
| Trained as NEG | 11 | 6 | 55% |

---

## Panel Judge Results (Opus + Sonnet + Haiku)

**N** = 23 debates judged

| Metric | Value |
|--------|-------|
| Trained wins | 10 / 23 (44%) |
| Base wins | 13 / 23 (56%) |
| Mean score diff | -0.9 (SD=13.8) |
| Binomial p-value | 0.6776  |
| Paired t-test p | 0.7580  |
| Cohen's d | -0.065 (negligible) |
| Significant (p<0.05)? | **NO** |
| Debates needed (power=0.80) | 1856 |

### Judge Agreement

- Unanimous: 12/23
- Majority:  11/23
- Split:     0/23

### Per-Model Voting

| Model | AFF Votes | NEG Votes | Errors |
|-------|-----------|-----------|--------|
| haiku | 7 | 16 | 0 |
| opus | 15 | 8 | 0 |
| sonnet | 8 | 15 | 0 |

### Side Bias

| Side | N | Trained Wins | Win Rate |
|------|---|-------------|----------|
| Trained as AFF | 12 | 4 | 33% |
| Trained as NEG | 11 | 6 | 55% |

---

## Per-Debate Results (Pipeline Judge)

| # | Debate ID | Trained Side | Won? | Score Diff | Re-run? |
|---|-----------|-------------|------|-----------|---------|
| 1 | v3_t10_trained_aff | AFF | LOSS | -19.2 | Yes |
| 2 | v3_t10_trained_neg | NEG | LOSS | -6.0 | Yes |
| 3 | v3_t11_trained_aff | AFF | LOSS | -7.0 |  |
| 4 | v3_t11_trained_neg | NEG | LOSS | -6.0 |  |
| 5 | v3_t12_trained_aff | AFF | LOSS | -2.8 |  |
| 6 | v3_t12_trained_neg | NEG | WIN | +28.0 |  |
| 7 | v3_t1_trained_aff | AFF | LOSS | +10.8 | Yes |
| 8 | v3_t1_trained_neg | NEG | WIN | +6.6 | Yes |
| 9 | v3_t2_trained_aff | AFF | LOSS | -8.0 |  |
| 10 | v3_t2_trained_neg | NEG | LOSS | -26.4 |  |
| 11 | v3_t3_trained_aff | AFF | LOSS | -19.6 |  |
| 12 | v3_t4_trained_aff | AFF | LOSS | -3.4 | Yes |
| 13 | v3_t4_trained_neg | NEG | WIN | +10.0 |  |
| 14 | v3_t5_trained_aff | AFF | LOSS | -28.0 |  |
| 15 | v3_t5_trained_neg | NEG | WIN | +20.0 |  |
| 16 | v3_t6_trained_aff | AFF | LOSS | -8.0 |  |
| 17 | v3_t6_trained_neg | NEG | LOSS | -11.0 |  |
| 18 | v3_t7_trained_aff | AFF | WIN | +26.0 |  |
| 19 | v3_t7_trained_neg | NEG | WIN | +26.0 |  |
| 20 | v3_t8_trained_aff | AFF | LOSS | -20.0 |  |
| 21 | v3_t8_trained_neg | NEG | LOSS | -3.0 | Yes |
| 22 | v3_t9_trained_aff | AFF | LOSS | -20.0 |  |
| 23 | v3_t9_trained_neg | NEG | WIN | +12.0 |  |

---

## Interpretation

The fine-tuned model actually performs WORSE than base (30% win rate, p=0.0931).

## Methodology

- Both models served via vLLM on Modal (A100-80GB)
- Full IPDA debate pipeline with reused belief trees
- Per-speech dimensional judging + meta-judge (pipeline score)
- 3-model panel: Opus 4.5, Sonnet 4, Haiku 4.5 (all Bedrock)
- 10 balanced topics, each debated with trained model on both sides
- Side-blind judging (judges don't know which model is which)