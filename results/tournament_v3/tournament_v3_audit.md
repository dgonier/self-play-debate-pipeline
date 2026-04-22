# Tournament V3 Audit Report

**Date**: 2026-02-18
**Purpose**: Identify all issues in tournament_v3 and determine what can be recovered

---

## Executive Summary

Tournament V3 has **three major categories of problems**:

1. **Panel Judge Failure (ALL 20 debates)**: Gemini 2.5 Pro and GPT-5.2 both failed with API key authentication errors on every single debate. The "3-model panel" was actually a 1-model (Opus-only) panel. All panel decisions labeled "unanimous" are misleading -- they reflect 1 vote, not 3.

2. **Null/Missing Speeches (7 of 20 debates)**: The debate engine failed to generate certain speeches (mostly NC constructives), leaving incomplete transcripts that judges evaluated anyway.

3. **Incorrect Winner Assignment**: The report's panel winner mapping (trained_won field) appears to be correctly computed from the data, but the data itself is unreliable because decisions came from a single judge evaluating sometimes-incomplete debates.

---

## Problem 1: Panel Judge Authentication Failures

### What happened
- **Gemini 2.5 Pro**: `API key not valid` (HTTP 400) on all 20 debates
- **GPT-5.2**: `OPENAI_API_KEY environment variable` not set on all 20 debates
- **Opus (Bedrock)**: Worked fine on all 20 debates

### Impact
- Every "panel" decision = single Opus vote
- `"agreement": "unanimous"` on all 20 debates (1/1 voters agree with themselves)
- Opus shows a **NEG-side bias**: picked NEG in 13/20 debates (65%)
- Opus has a **narrow scoring range**: 16/20 debates scored exactly 78/72 or 72/78
- The entire purpose of a multi-model panel (reducing single-model bias) was defeated

### What exists for rejudging
- **`rejudge_v3_fast` (completed)**: Used Sonnet + Haiku + Opus (all Bedrock). Successfully rejudged 15/20 debates (the 15 that were available at time of run). Result: trained 10/15 (67%), not significant (p=0.30).
- **`debiased_all` (completed)**: Tested debiased judging prompts on all 20 debates with Opus + Sonnet + Haiku. Found NEG-side bias was real (~53% NEG preference without debiasing).
- **`rejudge_v3` (abandoned)**: Tried to use Gemini/GPT again, was killed after 14 lines.

---

## Problem 2: Null/Missing Speeches

7 of 20 debates have at least one null speech. The speech generation pipeline step (`SPEECH_GENERATE`) silently failed after the preparation steps (TACTIC_SELECT, SKELETON_BUILD, EVIDENCE_SELECT) completed.

| Debate ID | Topic | Null Speeches | Speeches OK | Severity |
|-----------|-------|---------------|-------------|----------|
| v3_t1_trained_aff | Free will compatible with determinism | NC | 6/7 | Medium |
| v3_t1_trained_neg | Free will compatible with determinism | NC | 6/7 | Medium |
| v3_t3_trained_neg | Moral truths are objective facts | 1AR | 6/7 | Medium |
| v3_t4_trained_aff | The ends can justify the means | AC, 1AR | 5/7 | **HIGH** |
| v3_t8_trained_neg | Compulsory voting strengthens democracy | 2AR | 6/7 | Medium |
| v3_t10_trained_aff | Direct instruction > inquiry-based learning | NC | 6/7 | Medium |
| v3_t10_trained_neg | Direct instruction > inquiry-based learning | NC | 6/7 | Medium |

**Notable anomaly**: When NC is null, the NC-CX still has content -- the cross-examination answers reference arguments that never appeared in the actual NC speech. The debate engine used planning/skeleton data instead of the speech text.

**v3_t4_trained_aff is the worst case**: Missing both AC and 1AR (the trained model's two speeches!), leaving only 5/7 speeches. The trained model essentially had no voice in this debate yet was still scored.

---

## Problem 3: What the Report Claims vs Reality

### Pipeline Judge (inline scoring + meta-judge)
| Metric | Reported | Accurate? |
|--------|----------|-----------|
| Trained wins: 9 | 9/20 | Yes, but 7 debates had null speeches |
| Base wins: 11 | 11/20 | Yes, but 7 debates had null speeches |
| Win rate: 45% | Correct | Correct math, questionable data |

### Panel Judge (claimed "Opus 4.5 + Gemini 2.5 Pro + GPT-5.2")
| Metric | Reported | Accurate? |
|--------|----------|-----------|
| Trained wins: 10 | 10/20 | **Misleading** -- Opus-only decisions |
| Base wins: 10 | 10/20 | **Misleading** -- Opus-only decisions |
| "unanimous" agreement | All 20 | **False** -- 1/3 judges voted, 2/3 errored |

---

## Debate-by-Debate Inventory

### Legend
- **Transcript**: COMPLETE = all 7 speeches present, PARTIAL = some null speeches
- **Pipeline**: Who the pipeline meta-judge said won (trained/base)
- **Opus Panel**: Who the sole working panel judge (Opus) said won
- **Rejudge**: Result from rejudge_v3_fast (Sonnet+Haiku+Opus panel) if available
- **Needs Rejudge?**: Whether this debate needs proper panel rejudging

| # | Debate ID | Topic | Trained Side | Transcript | Null Speeches | Pipeline Winner | Opus Panel Winner | Pipeline/Panel Agree? | Rejudged? | Needs Work? |
|---|-----------|-------|-------------|------------|---------------|----------------|-------------------|----------------------|-----------|-------------|
| 1 | v3_t1_trained_aff | Free will & determinism | AFF | PARTIAL | NC | BASE | TRAINED | NO | Yes (fast) | Rejudge OK, but null NC |
| 2 | v3_t1_trained_neg | Free will & determinism | NEG | PARTIAL | NC | TRAINED | TRAINED | YES | Yes (fast) | Rejudge OK, but null NC |
| 3 | v3_t2_trained_aff | Criminal punishment | AFF | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 4 | v3_t2_trained_neg | Criminal punishment | NEG | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 5 | v3_t3_trained_aff | Moral truths objective | AFF | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 6 | v3_t3_trained_neg | Moral truths objective | NEG | PARTIAL | 1AR | TRAINED | TRAINED | YES | Yes (fast) | Rejudge OK, but null 1AR |
| 7 | v3_t4_trained_aff | Ends justify means | AFF | **PARTIAL** | **AC, 1AR** | BASE | BASE | YES | Yes (fast) | **UNRELIABLE -- 2 null speeches** |
| 8 | v3_t4_trained_neg | Ends justify means | NEG | COMPLETE | -- | TRAINED | TRAINED | YES | Yes (fast) | Rejudge OK |
| 9 | v3_t5_trained_aff | Nuclear proliferation | AFF | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 10 | v3_t5_trained_neg | Nuclear proliferation | NEG | COMPLETE | -- | TRAINED | TRAINED | YES | Yes (fast) | Rejudge OK |
| 11 | v3_t6_trained_aff | 4-day workweek | AFF | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 12 | v3_t6_trained_neg | 4-day workweek | NEG | COMPLETE | -- | BASE | BASE | YES | Yes (fast) | Rejudge OK |
| 13 | v3_t7_trained_aff | Remote work productivity | AFF | COMPLETE | -- | TRAINED | BASE | NO | Yes (fast) | Rejudge OK |
| 14 | v3_t7_trained_neg | Remote work productivity | NEG | COMPLETE | -- | TRAINED | TRAINED | YES | Yes (fast) | Rejudge OK |
| 15 | v3_t8_trained_aff | Compulsory voting | AFF | COMPLETE | -- | BASE | TRAINED | NO | Yes (fast) | Rejudge OK |
| 16 | v3_t8_trained_neg | Compulsory voting | NEG | PARTIAL | 2AR | BASE | TRAINED | NO | No | **Needs rejudge + null 2AR** |
| 17 | v3_t9_trained_aff | Trade & war | AFF | COMPLETE | -- | BASE | TRAINED | NO | No | **Needs rejudge** |
| 18 | v3_t9_trained_neg | Trade & war | NEG | COMPLETE | -- | TRAINED | BASE | NO | No | **Needs rejudge** |
| 19 | v3_t10_trained_aff | Direct instruction | AFF | PARTIAL | NC | TRAINED | BASE | NO | No | **Needs rejudge + null NC** |
| 20 | v3_t10_trained_neg | Direct instruction | NEG | PARTIAL | NC | TRAINED | TRAINED | YES | No | **Needs rejudge + null NC** |

---

## Recovery Assessment

### What we HAVE (good data)
- **13 debates with complete transcripts** that can be properly rejudged
- **15 debates already rejudged** with the Bedrock panel (Sonnet+Haiku+Opus) via `rejudge_v3_fast`
- **20 debates with debiased judging** results (Opus+Sonnet+Haiku, old vs new prompts)
- Full debate transcripts (speeches) preserved in both regular and `_full` JSON files
- All belief trees, call records, and distillation bundles in `_full` files

### What we DON'T HAVE
- **Any valid Gemini or GPT judging** -- 0/40 attempted judgments succeeded
- **5 debates not yet rejudged** with the Bedrock panel (t8_neg, t9_aff, t9_neg, t10_aff, t10_neg)
- **Complete transcripts for 7 debates** -- null speeches cannot be regenerated

### What NEEDS to happen
1. **Rejudge the remaining 5 debates** with the Bedrock panel (Sonnet+Haiku+Opus) to get consistent 3-judge panel results across all 20 debates
2. **Decide how to handle the 7 debates with null speeches**:
   - Option A: Exclude them from analysis (leaves 13 clean debates)
   - Option B: Keep them but flag them (judges evaluated what was available)
   - Option C: Re-run those 7 debates entirely (requires debate engine + models)
3. **Consider adding non-Anthropic judges** if Gemini/GPT API keys can be configured correctly
4. **Recompute tournament statistics** using only reliable data

### Recommended Action Plan

**Phase 1 -- Quick fix (rejudge 5 remaining debates with Bedrock)**
- Rejudge: v3_t8_trained_neg, v3_t9_trained_aff, v3_t9_trained_neg, v3_t10_trained_aff, v3_t10_trained_neg
- Use same Bedrock panel as rejudge_v3_fast (Sonnet + Haiku + Opus)
- This gives us consistent 3-judge results for all 20 debates

**Phase 2 -- Recompute results**
- Split results into "clean" (13 complete transcripts) and "flagged" (7 with null speeches)
- Report both: full 20-debate results and clean-only 13-debate results
- Use the rejudge_v3_fast panel results (not the broken original panel)

**Phase 3 -- Optional improvements**
- Fix Gemini/GPT API keys and add them as additional judges for diversity
- Re-run the 7 broken debates if the debate engine is available
- Consider the debiased prompt as the standard going forward (it surfaced real NEG bias)

---

## Appendix: Rejudge Results (rejudge_v3_fast, 15 debates)

From the completed Bedrock panel rejudging:

| Debate ID | Trained Side | Panel Winner | Trained Won | Agreement | Null Speeches |
|-----------|-------------|-------------|-------------|-----------|---------------|
| v3_t10_trained_neg | NEG | neg | Yes | unanimous | NC |
| v3_t7_trained_aff | AFF | neg | No | majority | -- |
| v3_t5_trained_neg | NEG | neg | Yes | unanimous | -- |
| v3_t4_trained_aff | AFF | neg | No | unanimous | AC, 1AR |
| v3_t2_trained_neg | NEG | neg | Yes | unanimous | -- |
| v3_t4_trained_neg | NEG | neg | Yes | majority | -- |
| v3_t3_trained_aff | AFF | neg | No | unanimous | -- |
| v3_t2_trained_aff | AFF | neg | No | unanimous | -- |
| v3_t3_trained_neg | NEG | neg | Yes | unanimous | 1AR |
| v3_t6_trained_neg | NEG | neg | Yes | majority | -- |
| v3_t5_trained_aff | AFF | neg | No | unanimous | -- |
| v3_t6_trained_aff | AFF | aff | Yes | majority | -- |
| v3_t1_trained_aff | AFF | aff | Yes | majority | NC |
| v3_t7_trained_neg | NEG | neg | Yes | majority | -- |
| v3_t1_trained_neg | NEG | neg | Yes | unanimous | NC |
| v3_t8_trained_aff | AFF | aff | Yes | unanimous | -- |

**Rejudge totals**: Trained 10/15 (67%), Base 5/15 (33%)
**NEG side bias**: NEG won 10/15 (67%) -- strong NEG bias persists even with 3-judge Bedrock panel

---

## Appendix: Opus NEG-Side Bias (Original Panel)

Opus picked NEG winner in 13/20 debates (65%). This is consistent with the debiased analysis finding that old (non-debiased) prompts favored NEG 53%, shifting to AFF 55% with debiased prompts.

Opus scores nearly always 78/72 or 72/78 (winner/loser), suggesting a narrow dynamic range that may not capture the actual quality differences between debates.
