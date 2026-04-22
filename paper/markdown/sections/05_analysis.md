# Analysis and Discussion

#### Side asymmetry.

The trained model wins 67.6% as negative but only 41.2% as affirmative; the base model shows the
same direction (58.8% vs. 32.4%), indicating a structural IPDA negative-side advantage amplified by
training. GRPO reward is dominated by reactive rebuttals, which produce higher-variance outputs and
thus richer preference signal than constructive case-building. More broadly, *preference
optimization on multi-role tasks may systematically favor roles where contrastive quality
differences are larger*—relevant to any task combining critique and creation (code review
vs. generation, red-teaming vs. safety training).

#### Dialogue resists monologue training.

CX scores stayed flat through 12 iterations of speech-focused training; hindsight retries actually
*degraded* CX by 60–85%. Group-wise GRPO
(Section [ref:sec:phase3])
confirms dialogue and monologue require fundamentally different optimization.

#### Training failure modes.

Three failure modes with broader RLAIF implications
(Appendix [ref:app:failure_modes]): (1) *feedback hallucination* (35.6% of
thinking sections hallucinated judge criticism, resolved via self-coaching framing); (2) *retry
assumption failure* (retries outperformed originals only 45% of the time); (3) *GRPO regression on
MoE*—short-form CX training penalized long-form output, fixed by attention-only LoRA.

#### Limitations.

Scoring uses LLM judges with no human calibration. Results are specific to IPDA; generalization
requires validation. With 68 debates, statistical power is limited ($\sim$<!-- -->30% for medium
effects). Sonnet 4 is the sole training judge, though non-Sonnet evaluation confirms the advantage
($p = 0.014$). All experiments use a single base model (Qwen3-30B-A3B).
