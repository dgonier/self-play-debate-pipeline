# Experiments

## Training Setup

We train Qwen3-30B-A3B, a mixture-of-experts model with 30B total and 3B active parameters, on 30
IPDA topics spanning STEM, humanities, and policy. All training runs on an AWS p4de.24xlarge
(8$\times$A100 80GB). Inline speech scoring uses Claude Sonnet 4; retrospective debate-level
evaluation uses a 3-model panel (Claude Opus 4.5, Gemini 2.5 Pro, GPT-5.2). Total compute cost
across all iterations was approximately \$750–\$1,000 (see
Appendix [ref:app:experiment_details] for full hyperparameters and
cost breakdown).

Training proceeds via group-wise offline GRPO
(Section [ref:sec:grpo]),
partitioning calls into four groups trained sequentially within each iteration.

## Group-Wise GRPO Results

<div id="tab:phase1">

| **Group** | **Call Types**                                   | **Samples** | **Val Acc** |     **Key Finding**      |
|:----------|:-------------------------------------------------|------------:|:-----------:|:------------------------:|
| A         | <span class="smallcaps">tactic_select</span>     |       2,887 |    81.0%    |   Stable steps 200–500   |
| B         | <span class="smallcaps">skeleton+evidence</span> |       4,157 |    73.3%    |  Logprob recompute req.  |
| C         | <span class="smallcaps">speech_generate</span>   |       3,274 |    72.3%    | Attn-only LoRA critical  |
| D         | <span class="smallcaps">cx_dialogue</span>       |       5,003 |    87.5%    | No overfit (93.6% train) |

Per-group GRPO training results. Each group trains sequentially on the canonical model produced by
the previous group’s merge. Validation accuracy is measured on held-out debates not seen during
training. Group D (cross-examination) achieves the highest validation accuracy despite being the
most interactive modality.

</div>

Table [ref:tab:phase1] summarizes
training across the four groups. Key findings for applying GRPO to MoE architectures: (1) mixing all
call types in a single run caused short tactics to dominate gradients, degrading speech
quality—group-wise training isolates each modality; (2) Group C diverged under full LoRA (3.37B
params) but stabilized with attention-only LoRA (53M params, 63$\times$ reduction), suggesting MoE
routing weights are unsafe to modify via LoRA; (3) logprobs must be recomputed after each group
merge to prevent stale reference distributions (4.2% accuracy drop otherwise); (4) CX achieved the
highest validation accuracy (87.5%) despite being the most interactive modality, due to clearer
quality signal.

## Speech-Level Progression

All speech types improve monotonically across iterations, with negative speeches (NC, NR) starting
stronger and plateauing earlier than affirmative speeches—foreshadowing the tournament side
asymmetry. CX scores remained flat (0.40–0.50) through iteration 8, then jumped to 0.65–0.75 after
Group D GRPO training, confirming that dialogue requires modality-specific optimization.
Per-speech-type score progressions are in
Appendix [ref:app:experiment_details].

## Head-to-Head Tournament Evaluation

We conducted a 68-debate tournament (17 held-out topics $\times$ 4 debates each, balanced by side)
comparing the trained model against the base Qwen3-30B-A3B, both using identical inference with no
golden fallback. Each debate is scored by 5 judges: the pipeline judge (Sonnet 4) and a panel of
Opus 4.5, Sonnet 4, Gemini 2.5 Pro, and GPT-5.2, with bias detection and retry on inconsistencies.

Tournament topics were selected to minimize judge-model side bias. From a corpus of 54 candidate
resolutions, we asked three judge models (Opus, Gemini, GPT) to rate each on a 0–10 scale (0 =
complete NEG support, 5 = neutral, 10 = complete AFF support) and selected the 17 topics whose mean
rating was closest to 5.0 across all three models
(Appendix [ref:app:tournament_details]).

<div id="tab:tournament">

| **Judge System**     | **Trained Wins** | **Win%**  |    **95% CI**    |   $p$    |
|:---------------------|:----------------:|:---------:|:----------------:|:--------:|
| Pipeline (Sonnet)    |      37/68       |   54.4%   |   \[.43, .66\]   |   .545   |
| Panel (majority)     |      38/68       |   55.9%   |   \[.44, .67\]   |   .396   |
| Debate majority      |      41/68       |   60.3%   |   \[.48, .71\]   |   .057   |
| **All judges (GEE)** |   **198/340**    | **58.2%** | **\[.51, .66\]** | **.034** |

Tournament results (68 debates). GEE with exchangeable correlation clustered on debate accounts for
within-debate vote dependence ($p = 0.034$); debate-level majority vote yields 41/68 ($p = 0.057$).
A permutation test at the debate level confirms significance ($p = 0.020$). The effect size is small
(Cohen’s $d = 0.166$), consistent with early-stage preference optimization on a challenging
multi-turn task.

</div>

Table [ref:tab:tournament]
reports the primary result: the trained model wins 58.2% of all judge votes (GEE clustered on
debate, $p = 0.034$). The score differential distribution is right-skewed (mean $+2.7$;
Appendix [ref:app:tournament_details]), indicating the trained model
wins by larger margins than it loses. Using only non-Sonnet judges (Opus, Gemini, GPT; 204 votes),
the trained model wins 58.8% ($p = 0.014$, binomial), confirming that the advantage generalizes
beyond the reward model.

#### Side asymmetry.

The trained model wins 67.6% as negative but only 41.2% as affirmative
(Table [ref:tab:side_asymmetry]).
The base model shows the same directional bias (58.8% NEG vs. 32.4% AFF), indicating a structural
IPDA advantage amplified by training. Among non-Sonnet judges, the asymmetry persists (69.6% NEG
vs. 48.0% AFF, $p = 0.003$). We analyze why in
Section [ref:sec:analysis].

<div id="tab:side_asymmetry">

| **Trained Side**              | **Wins**  | **Win%**  | **Mean $\Delta$** |   $p$    |
|:------------------------------|:---------:|:---------:|:-----------------:|:--------:|
| Affirmative                   |   14/34   |   41.2%   |      $-3.4$       |   .392   |
| **Negative**                  | **23/34** | **67.6%** |      $+8.9$       |   .058   |
| Side difference (Welch’s $t$) |           |           |   $\Delta=12.3$   | **.002** |

Performance by debate side. The trained model’s negative-side advantage parallels the base model’s
own NEG preference, suggesting a structural IPDA side effect amplified by preference optimization.

</div>

#### Dimensional analysis.

Decomposing per-call scores
(Figure [ref:fig:baseline_vs_experimental]) clarifies *where* the trained model improves.
It beats the base on all four judged dimensions with small-to-moderate effects: argument $+0.045$
($d{=}0.26$), clash $+0.051$ ($d{=}0.29$), language $+0.035$ ($d{=}0.29$), evidence $+0.025$
($d{=}0.12$). Pipeline-stage decomposition is sharper: tactic selection jumps
$0.156 \rightarrow 0.230$ ($+48\%$ relative, $d{=}0.30$), while skeleton ($-0.012$), evidence
($-0.024$), and execution ($+0.016$) are unchanged. This matches the hierarchical reward story:
Group A GRPO targets tactic and moves it the most; pipeline-fixed stages are near-identical across
debaters, consistent with the scaffolded prep pipeline driving baseline quality while sub-call GRPO
concentrates on decision points it can influence. The tactic gain concentrates on opening speeches
(AC: $+0.164$, $d{=}0.68$; NC: $+0.157$, $d{=}0.59$).

<figure id="fig:baseline_vs_experimental">
<embed src="fig_baseline_vs_experimental.pdf" />
<figcaption>Per-call dimensional scores (left) and pipeline stage rewards (right), trained vs. base
across 68 debates (bootstrap 95% CIs). Biggest delta is tactic selection (<span
class="math inline"> + 48%</span> relative), the stage directly touched by Group A sub-call
GRPO.</figcaption>
</figure>

#### Per-topic analysis.

The trained model excels on abstract and philosophical topics (7 of 17 $\geq$<!-- -->75% win rate)
but struggles on evidence-dense empirical claims. Full per-topic results are in
Appendix [ref:app:tournament_details].

#### Judge reliability.

Per-judge analysis (Appendix [ref:app:tournament_details]) reveals model-specific side
biases: GPT and Sonnet favor the negative debater (94%, 88% when trained argues NEG), while Gemini
shows the opposite (65% when trained argues AFF). These opposing biases partially cancel in panel
consensus (55.9%). Fleiss’ $\kappa = 0.229$ (fair agreement) underscores that no single LLM judge
should be trusted for adversarial evaluation.

## Ablation

The group-wise structure provides natural ablation points. **Tactic selection** (Group A, 81.0% val
acc) unlocks latent capabilities: the top 3 tactics achieve 100% success vs. 38% overall, showing
performance is bottlenecked by strategy retrieval, not capacity. **Attention-only LoRA** is critical
for MoE: Group C diverged under full LoRA (3.37B params) but stabilized at 53M params. **Branching**
counterfactual pairs receive $2\times$ GRPO weight; isolating branching’s contribution remains
future work.
