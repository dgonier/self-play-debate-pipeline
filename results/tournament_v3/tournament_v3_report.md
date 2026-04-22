# Tournament V3: Trained vs RAW Qwen3-30B-A3B

**Date**: 2026-02-18 03:40 UTC
**Trained**: `iter3-grpo-groupd` (SFT + GRPO A→D)
**Base**: `Qwen/Qwen3-30B-A3B-Thinking-2507` (RAW, untrained)
**Debates**: 20 (10 topics x 2 sides)
**Belief trees**: Reused from tournament v2
**Significant**: NO

## Pipeline Judge Results (inline scoring + meta-judge)

| Metric | Value |
|--------|-------|
| Trained wins | 9 |
| Base wins | 11 |
| Win rate | 45% |
| Mean score diff | -2.2 (std=16.2) |
| Binomial p | 0.8238 |
| T-test p | 0.5519 |

## 3-Model Panel Results (Opus 4.5 + Gemini 2.5 Pro + GPT-5.2)

| Metric | Value |
|--------|-------|
| Trained wins | 10 |
| Base wins | 10 |
| Win rate | 50% |
| Mean vote margin | -1.9 |
| Binomial p | 1.0000 |
| T-test p | 0.4492 |

## Per-Debate Results

| # | Debate | T-Side | Pipeline | Panel | Agreement | Score Diff |
|---|--------|--------|----------|-------|-----------|------------|
| 1 | v3_t10_trained_aff | AFF | WON | LOST | unanimous | +4.0 |
| 2 | v3_t10_trained_neg | NEG | WON | WON | unanimous | +12.5 |
| 3 | v3_t1_trained_aff | AFF | LOST | WON | unanimous | -3.0 |
| 4 | v3_t1_trained_neg | NEG | WON | WON | unanimous | +4.0 |
| 5 | v3_t2_trained_aff | AFF | LOST | LOST | unanimous | -8.0 |
| 6 | v3_t2_trained_neg | NEG | LOST | LOST | unanimous | -26.4 |
| 7 | v3_t3_trained_aff | AFF | LOST | LOST | unanimous | -19.6 |
| 8 | v3_t3_trained_neg | NEG | WON | WON | unanimous | +4.5 |
| 9 | v3_t4_trained_aff | AFF | LOST | LOST | unanimous | -7.0 |
| 10 | v3_t4_trained_neg | NEG | WON | WON | unanimous | +10.0 |
| 11 | v3_t5_trained_aff | AFF | LOST | LOST | unanimous | -28.0 |
| 12 | v3_t5_trained_neg | NEG | WON | WON | unanimous | +20.0 |
| 13 | v3_t6_trained_aff | AFF | LOST | LOST | unanimous | -8.0 |
| 14 | v3_t6_trained_neg | NEG | LOST | LOST | unanimous | -11.0 |
| 15 | v3_t7_trained_aff | AFF | WON | LOST | unanimous | +26.0 |
| 16 | v3_t7_trained_neg | NEG | WON | WON | unanimous | +26.0 |
| 17 | v3_t8_trained_aff | AFF | LOST | WON | unanimous | -20.0 |
| 18 | v3_t8_trained_neg | NEG | LOST | WON | unanimous | -13.0 |
| 19 | v3_t9_trained_aff | AFF | LOST | WON | unanimous | -20.0 |
| 20 | v3_t9_trained_neg | NEG | WON | LOST | unanimous | +12.0 |

## Side Analysis

| Metric | Pipeline | Panel |
|--------|----------|-------|
| Trained as AFF: wins | 2/10 | 3/10 |
| Trained as NEG: wins | 7/10 | 7/10 |

## Methodology

- Both models served via vLLM (TP=4, max-model-len=32768)
- Full debate pipeline with reused belief trees from tournament v2
- Per-speech dimensional judging + meta-judge for pipeline score
- 3-model panel: Opus 4.5 (Bedrock), Gemini 2.5 Pro, GPT-5.2
- 10 balanced topics, each debated with trained model playing each side
- **CRITICAL FIX**: v2 used iter1-base (already fine-tuned) as base. v3 uses actual raw Qwen.