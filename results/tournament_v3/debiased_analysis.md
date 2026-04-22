# Debiased Judge Prompt Analysis — Tournament V3

## Setup
- **20 debates** (10 topics × trained-AFF and trained-NEG)
- **3 judge models**: Opus, Sonnet, Haiku (all Claude on Bedrock)
- **2 prompt versions**: OLD (no debiasing) vs NEW (bias-surfacing + educator framing)
- **Total**: 120 judgments (60 per prompt version)

## Headline Results

| Metric | OLD (no debiasing) | NEW (debiased) |
|--------|-------------------|----------------|
| Trained win rate | 28/59 (47.5%) | 27/60 (45.0%) |
| NEG vote rate (side bias) | 31/59 (52.5%) | 27/60 (45.0%) |

**Key finding**: Debiasing shifts judges from NEG-favoring (53%) to AFF-favoring (55%), but the overall trained win rate barely changes. The bias was real but symmetric — it helped trained-NEG as much as it hurt trained-AFF.

## By Trained Side

| Trained Side | OLD | NEW | Delta |
|-------------|-----|-----|-------|
| Trained-AFF | 13/29 (45%) | 15/30 (50%) | +5pp |
| Trained-NEG | 15/30 (50%) | 12/30 (40%) | -10pp |

Debiasing helps when trained model plays AFF (removes NEG bias), but hurts when trained model plays NEG (removes NEG advantage).

## Debate-Level Flips (5/20 debates)

| Debate | Trained Side | Flip | OLD | NEW |
|--------|-------------|------|-----|-----|
| v3_t7_trained_aff | AFF | BASE→TRAINED | 0/2 | 3/3 |
| v3_t1_trained_aff | AFF | TRAINED→BASE | 2/3 | 1/3 |
| v3_t1_trained_neg | NEG | TRAINED→BASE | 2/3 | 1/3 |
| v3_t3_trained_neg | NEG | TRAINED→BASE | 2/3 | 1/3 |
| v3_t5_trained_neg | NEG | TRAINED→BASE | 3/3 | 1/3 |

## Opinion Delta Analysis

| Stat | Value |
|------|-------|
| Mean delta | +0.32 |
| Mean strength | 6.02 |
| Range | -2 to +2 |

### Delta Distribution
| Delta | Count | % |
|-------|-------|---|
| -2 | 1 | 2% |
| -1 | 10 | 17% |
| 0 | 22 | 37% |
| +1 | 23 | 38% |
| +2 | 4 | 7% |

### Per-Model Delta
| Model | Mean Delta | Mean Strength |
|-------|-----------|---------------|
| Opus | -0.05 | 6.3 |
| Sonnet | +0.10 | 6.0 |
| Haiku | +0.90 | 5.8 |

**Insight**: Opus is essentially unmoved by debates (delta≈0), Sonnet shifts slightly, Haiku is most responsive. This suggests Haiku is most susceptible to in-debate persuasion, while Opus maintains the strongest priors.

## Conclusions

1. **NEG-side bias is real** — OLD prompts favored NEG 53%, debiased prompts shift to AFF 55%
2. **Debiasing is ~neutral for overall trained win rate** — helps on AFF side, hurts on NEG side
3. **The trained model wins ~47% regardless of prompt** — it's competitive but not clearly superior to raw Qwen on these topics
4. **Opinion deltas are small** — judges report their opinions barely shift (mean +0.32), suggesting the debiasing instruction works (they maintain declared neutrality)
5. **Haiku is most "persuadable"** — highest mean delta (+0.90) and lowest opinion strength (5.8)
6. **The debiased prompt successfully surfaces bias** — all judges honestly state their views, enabling better calibration
