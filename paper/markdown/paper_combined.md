# Can LLMs Improve at Debate Through Self-Play?
## A Pipeline and RL System to Gamify Competitive Debate with Branching and Hierarchical Rewards

*Anonymous Authors — NeurIPS 2026 submission*

---

> **Note:** This combined file is auto-generated from the per-section markdown mirror in `paper/markdown/sections/` and `paper/markdown/appendix/`. Each section below is preceded by a `> from:` annotation pointing to the original file. The `.tex` files in `paper/sections/` and `paper/appendix/` are the source of truth; this combined view exists for cross-section reading and search.

---

## Table of Contents

### Body
1. [Introduction](#introduction)
2. [Related Work](#related-work)
3. [Method](#method)
4. [Experiments](#experiments)
5. [Analysis](#analysis)
6. [Conclusion](#conclusion)

### Appendices
- [A. Method details](#a-method-details)
- [B. Experiment details](#b-experiment-details)
- [C. Tournament details](#c-tournament-details)
- [D. Failure modes](#d-failure-modes)
- [E. Hyperparameters](#e-hyperparameters)
- [F. Costs](#f-costs)
- [G. Debate examples](#g-debate-examples)
- [H. Branching](#h-branching)
- [I. Agentic judge](#i-agentic-judge)
- [J. GRPO groups](#j-grpo-groups)
- [K. Trajectory](#k-trajectory)
- [L. Pipeline](#l-pipeline)

---

# Body

> **from:** `paper/markdown/sections/01_introduction.md`  →  tex: `paper/sections/01_introduction.tex`

# Introduction

Competitive debate remains one of the most demanding language tasks: debaters must construct novel
arguments from evidence, anticipate and dismantle opposing positions, and adapt strategy in real
time across multiple speech acts. IBM’s Project Debater [cite:slonim2021debater] demonstrated that
AI systems could engage in simplified debate formats, but acknowledged fundamental limitations in
handling the “open-ended, complex” reasoning required for expert-level competitive debate. This has
led to skepticism about whether debate—unlike chess or Go—is amenable to systematic optimization.

We challenge this view. Using the International Public Debate Association (IPDA) format as a
testbed, we present a training pipeline that treats structured multi-turn generation as a search
problem. Each IPDA debate comprises a 7-speech sequence with ${\sim}33$ individual LLM calls (tactic
selection, argument structuring, evidence selection, speech generation, cross-examination), and our
system generates, scores, and optimizes across all of them. IPDA provides an ideal experimental
setting: explicit rules and evaluable criteria from specialist judges. As in competitive debate more
broadly, arguments follow typed structures (e.g., Advantage = Uniqueness + Link + Impact) that make
individual decisions legible to automated scoring.

On top of a fully automated prep pipeline (belief-tree construction, consolidated research,
sentence-level-traceable evidence cards), we branch the debate at each speech point into parallel
trajectories whenever candidates diverge enough that opponents would respond differently.
Winner-shifts between branches identify which specific decisions changed the outcome, producing
counterfactual training pairs with causal attribution. A three-layer hierarchical reward scores
speeches inline, backpropagates debate outcomes to the individual calls that caused them, and
applies multi-model retrospective analysis. These rewards feed a group-wise offline GRPO loop that
trains heterogeneous call modalities without cross-modality interference.

Along the way, our process surfaces practical RLAIF failure modes: feedback hallucination in
retry-based preference generation (35.6% contamination), inverted preference labels (55% of early
pairs), and catastrophic regression from training short-form dialogue alongside long-form speeches
on Mixture-of-Experts architectures.

#### Contributions.

1.  **End-to-end debate generation pipeline.** A fully automated pipeline turns a resolution into a
    grounded debate: Bayesian belief-tree construction, a consolidated research loop (2 LLM calls
    per hop vs. 9 in prior systems), evidence cards with sentence-level traceability preventing
    fabrication, and side-specific perspective building with typed arguments. Shared between
    baseline and experimental models, isolating training effects from prep quality.

2.  **Branching counterfactual credit assignment.** Debates are generated as branching trees: when
    candidate speeches diverge enough that opponents would respond differently, we explore both
    paths. Winner-shifts yield counterfactual training pairs with causal attribution of
    outcome-changing decisions.

3.  **Hierarchical reward with outcome backpropagation.** Three scoring layers—dimensional speech
    judging, outcome backpropagation to pipeline calls, and meta-debate comparison—enable
    fine-grained credit assignment to the ${\sim}33$ decisions per debate.

4.  **Group-wise offline GRPO for heterogeneous outputs.** Calls are decomposed into four modality
    groups (tactic, structure, speech, dialogue) and trained sequentially with SFT-on-golden
    interleaving and importance sampling, preventing cross-modality interference.

5.  **Tournament validation: 58.2% win rate ($p{=}0.034$, GEE).** Head-to-head evaluation on 68
    debates confirms the trained model outperforms the base, with top tactics achieving 100%
    success. We observe a structural side asymmetry (67.6% NEG vs. 41.2% AFF) and opposing judge
    biases that partially cancel in panel consensus.

---

> **from:** `paper/markdown/sections/02_related_work.md`  →  tex: `paper/sections/02_related_work.tex`

# Related Work

#### Computational Argumentation.

Project Debater [cite:slonim2021debater] demonstrated AI debate in a simplified format designed
for lay audiences, but explicitly acknowledged its inability to engage in expert competitive debate.
Prior work in computational argumentation has focused on argument mining, stance detection, and
persuasion prediction rather than end-to-end debate generation, and large-scale resources such as
OpenDebateEvidence [cite:roush2024opendebateevidence] have primarily supported evidence retrieval
and summarization rather than trained debaters. We target the International Public Debate
Association (IPDA) format as an instance of competitive debate more broadly. Competitive debate
formats share typed argument structures (Advantage = Uniqueness + Link +
Impact [cite:snider2008code]), explicit rules, and specialist judges; we argue that these
structured competitive formats provide the discrete rewards needed for optimization.

#### Self-Play and Search in Games.

Our branching mechanism draws on the tradition of self-play and tree search in game-playing AI.
AlphaGo Zero [cite:silver2017mastering] and AlphaZero [cite:silver2018general] achieve
superhuman performance via Monte Carlo tree search (MCTS) guided by learned value and policy
networks, while OpenAI Five [cite:berner2019dota] scaled self-play to the imperfect-information
setting of Dota 2. Unlike MCTS, which exhaustively explores game trees, our branching is triggered
only when candidate speeches would elicit different opponent responses, focusing computation on
informationally rich divergence points. This threshold-based branching is closer to selective search
in that it expands only the nodes where counterfactual outcomes are most likely to differ.

#### Tree Search with LLMs.

Similar branching ideas appear in other RL-for-generation domains. Tree of
Thoughts [cite:yao2023tree] expands reasoning trees at inference time using self-evaluation
heuristics, and RAP [cite:hao2023reasoning] treats an LLM as a world model and uses MCTS to search
over reasoning steps guided by value estimates. Our branching is related but operates on a different
signal: we branch based on *opponent-response divergence* during adversarial multi-agent rollouts
rather than on self-consistency or value estimates, and the resulting winner-shift events become
training targets for offline GRPO rather than an inference-time search procedure.

#### RL with Verifiable Rewards.

Recent work on reasoning-oriented RL trains with programmatically verifiable reward signals.
DeepSeek-R1 [cite:guo2025deepseekr1] demonstrates that large-scale RL with rule-based rewards
elicits strong chain-of-thought behaviors without supervised warm-start. Our three-layer reward
hierarchy occupies a middle ground: speech-level rubrics and branch-based winner-shift detection
provide near-verifiable local signals, while retrospective multi-model panels handle the
non-verifiable strategic quality of full debates.

#### Debate as AI Alignment.

Irving et al. [cite:irving2018debate] proposed debate as a scalable oversight mechanism, where
competing agents help judges identify truthful answers. Michael et al. [cite:michael2023debate]
showed that debate achieves 84% judge accuracy versus 74% for consultancy, with debate errors
decreasing with debater skill. Du et al. [cite:du2024multiagent] demonstrated that multi-agent
debate improves factuality through convergence dynamics. Our work complements this line by studying
the *training dynamics* of debate models rather than debate as an oversight protocol.

#### Constitutional AI and RLAIF.

RLAIF [cite:lee2024rlaif] replaces human annotators with LLM judges at 25–125$\times$ lower cost.
Constitutional AI [cite:bai2022constitutional] showed that models can self-critique and revise
outputs against a set of principles, enabling alignment without human preference labels. Our
hierarchical reward system extends this idea: rather than a single constitution, we employ
speech-specific rubrics at Layer 1, causal outcome attribution at Layer 2, and multi-model
retrospective judging at Layer 3, each providing a different form of AI-generated feedback.

#### Preference Optimization.

We build on ORPO [cite:hong2024orpo], which eliminates the reference model requirement of
DPO [cite:rafailov2023dpo], and offline GRPO [cite:shao2024deepseekmath], which uses importance
sampling ratios $\pi_\theta / \pi_{\text{ref}}$ to normalize for response length—critical for tasks
where quality does not correlate with verbosity. Our contribution is the *group-wise* application:
decomposing heterogeneous calls into four modality groups and training sequentially with
SFT-on-golden interleaving prevents the cross-modality interference we observe when training all
call types jointly.

#### LLM-as-Judge.

LLM judges achieve 80%+ human agreement but exhibit systematic biases [cite:zheng2023mtbench]:
position bias, verbosity preference, and self-enhancement. We document a novel bias pattern specific
to adversarial evaluation: different judge models exhibit *opposing side biases*
(Section [ref:sec:judge_bias]), motivating multi-model panels for debate
evaluation.

---

> **from:** `paper/markdown/sections/03_method.md`  →  tex: `paper/sections/03_method.tex`

# Method

## IPDA Debate Format

<div class="figure*">

<embed src="fig2_debate_sequence.pdf" />

</div>

IPDA consists of 7 speeches alternating between affirmative and negative (two constructives, two
cross-examinations, three rebuttals; Figure [ref:fig:debate_sequence]). This structure is a natural
curriculum: constructives require case generation, rebuttals require strategic response, and CX
requires real-time dialogue, motivating our group-wise training. Arguments follow typed syllogistic
structures drawn from standard debate theory [cite:snider2008code].

## Debate Generation Pipeline

Before any training innovation can operate, the system must first produce a complete, grounded
debate from only a resolution. Our preparation pipeline is the substrate on which branching,
hierarchical reward, and group-wise GRPO all operate, and it is shared identically between baseline
and experimental models, so downstream quality differences come from the speech generation model,
not from prep asymmetries.

**Belief tree.** A DSPy <span class="smallcaps">ValueExtractor</span> produces 4 topic-specific
values (2 per side); a <span class="smallcaps">BeliefGenerator</span> expands each to a depth-2 tree
($\sim$<!-- -->32 beliefs, $\sim$<!-- -->16 arguments per side). Each belief carries a Bayesian
credence in $[0,1]$, and arguments are typed (uniqueness, link, impact, solvency, turn) for
structured downstream slots. **Research loop.** Per argument claim: LLM query generation
$\rightarrow$ parallel Weaviate$+$Tavily retrieval $\rightarrow$ sentence chunking $\rightarrow$
hybrid scoring ($0.7\cdot\cos + 0.3\cdot$BM25) $\rightarrow$ window expansion $\rightarrow$
structured LLM selection. This consolidated loop uses **2 LLM calls per hop** vs. 9 in prior
systems, with most claims resolving in one hop. **Evidence cards** store `full_text`, `card` (with
**bolded** selections), `selected_sentence_ids`, and window ranges; speech generation cites by
sentence ID only, so quotations are assembled verbatim and fabrication is eliminated by
construction. **Perspective building.** A <span class="smallcaps">PerspectiveBuilder</span> compiles
side-specific prompts: constructives get pruned depth-1 beliefs (2 of 4); rebuttals get the full
sub-belief tree in SEAM form (Setup, Evidence, Analysis, Move). **Four-stage speech generation.**
Each of the 7 speeches runs (1) <span class="smallcaps">SelectTactic</span>,
(2) <span class="smallcaps">BuildSkeleton</span>, (3) <span class="smallcaps">SelectEvidence</span>
(constructives only; binds claims to sentence IDs), and
(4) <span class="smallcaps">GenerateSpeech</span>. The training innovations described next operate
on calls produced by this pipeline. Full schemas are in
Appendix [ref:app:pipeline].

## Branching Debate Generation

<div class="figure*">

<embed src="fig_branching_tree.pdf" />

</div>

Standard debate generation is linear: produce one speech, continue to the next. We instead treat
debate generation as **search over debate trajectories**
(Figure [ref:fig:branching_tree]). At each speech point, the model
generates $N = 3$ candidate trials scored by dimensional judges. When two or more trials exceed a
quality threshold *and* diverge sufficiently that the opponent would respond differently, the debate
forks into parallel paths (capped at 4 branches). The critical signal arises from **winner-shift
detection**: when branches from the same decision point produce different debate outcomes, we obtain
counterfactual training pairs that receive $2\times$ weight in GRPO
(Section [ref:sec:grpo]), isolating
the specific decision that changed the result. Before each speech, the model selects a named tactic
via an epsilon-greedy policy, serving as a commitment device that improves coherence. Full branching
thresholds and the state tracking algorithm are detailed in
Appendix [ref:app:branching].

## Hierarchical Reward System

<div class="figure*">

<embed src="fig_reward_hierarchy.pdf" />

</div>

Scoring isolated speeches is insufficient: a sound rebuttal can still lose if it addresses the wrong
arguments. We employ a three-layer reward hierarchy
(Figure [ref:fig:reward_hierarchy]).

#### Layer 1: Dimensional scoring.

Four sub-judges (ArgumentJudge, EvidenceJudge, ClashJudge, LanguageJudge) score each speech with
specialized rubrics, plus a speech-specific dimension reflecting strategic role (e.g., 1AR *triage
efficiency*, 2AR *crystallization*; Appendix [ref:app:agentic_judge]).

#### Layer 2: Outcome backpropagation.

A BackpropScorer propagates debate outcomes to individual calls with causal attribution, assigning
each speech a contribution in $[-1.0, +1.0]$. Winner-shift events from branching produce direct
adjustments at the divergence point, so a strong speech in a losing debate is not punished if the
loss originated earlier.

#### Layer 3: Meta-debate comparison.

A 3-model retrospective panel evaluates complete traces, detecting bias and identifying turning
points that become highest-signal training data.

#### Evidence verification.

Models cite by sentence ID, assembling verbatim text from research documents—eliminating fabrication
by construction. Evidence quality uses a 6-level scale with $2\times$ asymmetric GRPO penalty on
fabrications.

## Group-Wise Offline GRPO

<div class="algorithm">

<div class="algorithmic">

Generate debates with branching; capture log-probs Score with 3-layer reward hierarchy Generate Opus
golden samples for group SFT on golden $\rightarrow$ merge to SFT$^+$ Generate new trials with
SFT$^+$; capture log-probs Offline GRPO with importance sampling Merge LoRA $\rightarrow$ canonical
model

</div>

</div>

A debate produces $\sim$<!-- -->33 LLM calls spanning radically different output modalities:
$\sim$<!-- -->200-token tactic selections, $\sim$<!-- -->2,000-token speeches, and multi-turn CX.
Training jointly creates noisy gradients as the optimizer tries to satisfy contradictory length and
format distributions. We **decompose calls into four groups** processed sequentially each iteration
(Algorithm [ref:alg:training]):

<div id="tab:call_types">

| **Group** | **Call Types**                                                                                |    **Samples**     | **Output Length** |
|:----------|:----------------------------------------------------------------------------------------------|:------------------:|:-----------------:|
| A         | <span class="smallcaps">tactic_select</span>                                                  |  $\sim$<!-- -->3K  |       Short       |
| B         | <span class="smallcaps">skeleton_build</span>, <span class="smallcaps">evidence_select</span> |  $\sim$<!-- -->4K  |      Medium       |
| C         | <span class="smallcaps">speech_generate</span>                                                | $\sim$<!-- -->4.5K |       Long        |
| D         | <span class="smallcaps">cx_dialogue</span>                                                    |  $\sim$<!-- -->5K  |     Dialogue      |

Call-type groups for sequential GRPO training. Each group contains calls with similar output
modality and length distribution, preventing cross-modality gradient interference.

</div>

For each group, we: (1) generate Opus golden samples as quality upper bounds, (2) SFT on golden
samples via LoRA ($r = 32$) to produce an SFT$^+$ checkpoint, (3) generate new trials with SFT$^+$
while capturing log-probabilities for the behavior policy, (4) run offline
GRPO [cite:shao2024deepseekmath] with importance sampling, and (5) merge the LoRA into the
canonical model as baseline for the next group. Advantages are normalized within *(our_tactic,
opponent_tactic, opponent_intent)* triplets rather than globally, yielding cleaner gradient signal.
Full details are in Appendix [ref:app:grpo_groups].

#### Judge design.

Beyond the four Layer 1 sub-judges, a **Chronicler** tracks each argument’s status (standing,
attacked, dropped, extended, conceded, turned) across the debate, and a **Forensics module**
attributes failures to specific pipeline stages (tactic, skeleton, evidence, execution). For each
call, $N = 3$ trials at varied temperatures produce chosen/rejected preference pairs, yielding
$\sim$<!-- -->60+ pairs per debate (Appendix [ref:app:agentic_judge]).

---

> **from:** `paper/markdown/sections/04_experiments.md`  →  tex: `paper/sections/04_experiments.tex`

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

---

> **from:** `paper/markdown/sections/05_analysis.md`  →  tex: `paper/sections/05_analysis.tex`

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

---

> **from:** `paper/markdown/sections/06_conclusion.md`  →  tex: `paper/sections/06_conclusion.tex`

# Conclusion

We presented a system that treats structured multi-turn debate as search: an automated prep
pipeline, branching counterfactual credit assignment, a three-layer hierarchical reward over
${\sim}33$ calls, and group-wise offline GRPO. The trained model wins 58.2% of judge votes in a
68-debate tournament ($p = 0.034$, GEE). Four contributions generalize: (1) the prep pipeline
demonstrates that structured generation can be fully automated without human curation, enabling
rigorous baseline/experimental comparisons; (2) branching gives causal signal from winner-shifts;
(3) hierarchical reward enables fine-grained attribution; (4) modality-grouped training resolves
cross-modality interference. A structural side asymmetry (67.6% NEG vs. 41.2% AFF) suggests reactive
argumentation is more amenable to preference optimization than generative case construction. Total
cost: \$750–1,000
(Appendix [ref:app:costs]).
Future work: deeper branching, human expert evaluation, and targeted affirmative-side distillation.
Debate training carries dual-use risk, and the asymmetric role effect we document underscores the
need for per-role evaluation. Code and corpora: `[anonymized]`.

---

# Appendices

> **from:** `paper/markdown/appendix/appendix_a_method_details.md`  →  tex: `paper/appendix/appendix_a_method_details.tex`

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

---

> **from:** `paper/markdown/appendix/appendix_b_experiment_details.md`  →  tex: `paper/appendix/appendix_b_experiment_details.tex`

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

---

> **from:** `paper/markdown/appendix/appendix_c_tournament_details.md`  →  tex: `paper/appendix/appendix_c_tournament_details.tex`

# Tournament Details

This appendix provides the full tournament methodology and results for the head-to-head evaluation
referenced in Section [ref:sec:tournament]: the topic-selection procedure, per-topic
outcomes, score distributions, full statistical test battery, side-asymmetry and judge-bias
visualizations, and a comparison to an earlier tournament version.

## Topic Selection

The 17 tournament resolutions were selected from a corpus of 54 candidate topics through a
judge-bias probe. For each candidate, we queried three judge models (Claude Opus 4.5,
Gemini 2.5 Pro, and GPT-5.2) with the resolution and asked them to rate it on a 0–10 scale, where 0
indicates complete support for the negative position, 5 indicates a neutral topic with no
directional preference, and 10 indicates complete support for the affirmative. For each topic we
computed the mean rating across judges and the distance from 5.0; we selected the 17 topics with the
smallest distance as the tournament set.

A sample of selected topics with their bias distances:

- “The ends can justify the means” (dist: 0.17)

- “Mathematical objects exist independently of human minds” (dist: 0.17)

- “Deep learning will lead to artificial general intelligence” (dist: 0.17)

- “Moral truths are objective facts independent of human beliefs” (dist: 0.30)

- “Compulsory voting strengthens democracy” (dist: 0.80)

This approach identifies topics where the chosen judge models express no strong directional
preference; it does not eliminate all sources of bias. In particular, topics where judges are
systematically wrong in the same direction would appear unbiased by this metric but would still be
biased in absolute terms. The probing script is available at
`scripts/ipda_experiment/iter3/tournament/probe_topic_bias.py`.

## Per-Topic Results

| **Topic**                                     | **Wins** | **Win%** | **Mean $\Delta$** |
|:----------------------------------------------|:--------:|:--------:|------------------:|
| *Strong topics ($\geq$<!-- -->75% win rate)*  |          |          |                   |
| Moral truths are objective facts              |   3/4    |   75%    |           $+10.0$ |
| Economic development causes democratization   |   3/4    |   75%    |            $+9.6$ |
| Remote work reduces productivity              |   3/4    |   75%    |            $+8.4$ |
| Direct instruction $>$ inquiry-based learning |   3/4    |   75%    |            $+7.8$ |
| Compulsory voting strengthens democracy       |   3/4    |   75%    |            $+4.2$ |
| Economic sanctions are immoral                |   3/4    |   75%    |            $+3.0$ |
| Many-Worlds $>$ Copenhagen interpretation     |   3/4    |   75%    |            $+2.2$ |
| *Split topics (50% win rate)*                 |          |          |                   |
| The ends can justify the means                |   2/4    |   50%    |           $+11.5$ |
| Mathematical objects exist independently      |   2/4    |   50%    |           $+12.0$ |
| Voters capable of democratic accountability   |   2/4    |   50%    |            $+8.0$ |
| Language acquisition is primarily innate      |   2/4    |   50%    |            $+2.4$ |
| Eliminate teacher tenure                      |   2/4    |   50%    |            $-1.6$ |
| UBI should replace means-tested welfare       |   2/4    |   50%    |            $-4.6$ |
| *Weak topics ($\leq$<!-- -->25% win rate)*    |          |          |                   |
| Deep learning will lead to AGI                |   1/4    |   25%    |            $-4.1$ |
| Federal $>$ unitary government                |   1/4    |   25%    |            $-1.7$ |
| Saturated fat increases CVD risk              |   1/4    |   25%    |           $-13.5$ |
| International institutions constrain states   |   1/4    |   25%    |            $-7.4$ |

Per-topic tournament results (pipeline judge). The trained model excels on abstract/philosophical
topics but struggles on empirical/institutional topics.

## Score Distribution

<figure id="fig:score_distribution">
<embed src="fig_score_distribution.pdf" />
<figcaption>Distribution of score differentials (trained <span class="math inline">−</span> base)
across 68 debates. The distribution is right-skewed with mean <span
class="math inline"> + 2.7</span>, indicating the trained model tends to win by larger margins than
it loses.</figcaption>
</figure>

<div class="figure*">

<embed src="fig_topic_winrate.pdf" />

</div>

Pipeline judge mean score difference: $+2.72$ (SD $= 16.38$). The distribution is bimodal: the
trained model wins decisively when it wins (mean winning margin $+14.2$) but also loses decisively
on certain topic-side combinations (mean losing margin $-11.8$).

| **Score Diff Range**  | **Count** | **%** |
|:----------------------|:---------:|:-----:|
| Trained $+10$+        |    22     | 32.4% |
| Trained $+5$ to $+10$ |     8     | 11.8% |
| Trained $+0$ to $+5$  |     7     | 10.3% |
| Base $+0$ to $+5$     |    11     | 16.2% |
| Base $+5$ to $+10$    |    10     | 14.7% |
| Base $+10$+           |    10     | 14.7% |

Score difference distribution (pipeline judge).

## Statistical Tests

| **Test**                      | **Statistic**  | **$p$-value** |
|:------------------------------|:--------------:|:-------------:|
| Pipeline binomial (37/68)     |       –        |     0.545     |
| Panel binomial (38/68)        |       –        |     0.396     |
| Pooled binomial (198/340)     |       –        |     0.003     |
| Paired $t$-test (score diff)  | $t(67) = 1.37$ |     0.175     |
| Wilcoxon signed-rank          |  $W = 909.5$   |     0.107     |
| Cohen’s $d$ (pipeline)        |     0.166      |       –       |
| Side difference (Welch’s $t$) |   $t = 3.32$   |     0.002     |
| NEG wins binomial (23/34)     |       –        |     0.058     |
| AFF wins binomial (14/34)     |       –        |     0.392     |

Full statistical test battery for tournament results.

## Side Asymmetry Visualization

Figure [ref:fig:side_asymmetry]
visualizes the side-specific performance reported in
Table [ref:tab:side_asymmetry]. The asymmetry holds whether measured
by win rate (41.2% AFF vs. 67.6% NEG), mean score differential ($-3.4$ AFF vs. $+8.9$ NEG), or
Cohen’s $d$ by side (0.09 AFF vs. 0.48 NEG). Crucially, the base model also exhibits the same
directional pattern (32.4% AFF vs. 58.8% NEG from its own side perspective): the gap is structural
to IPDA, and training amplified rather than created it. We interpret this as evidence that reactive
argumentation (NEG, which speaks second and can respond to concrete AFF claims) is more amenable to
preference optimization than generative argumentation (AFF, which must build a case from scratch).

<figure id="fig:side_asymmetry">
<embed src="fig_side_asymmetry.pdf" />
<figcaption>Trained model win rate by debate side (pipeline judge, 68 debates). The 26.4
percentage-point gap between affirmative (41.2%) and negative (67.6%) win rates reflects a
structural IPDA side advantage amplified by training.</figcaption>
</figure>

## Judge Bias Analysis

<div id="tab:judge_bias">

| **Judge**  | **Trained%** | **As AFF** | **As NEG** | **Retries** |
|:-----------|:------------:|:----------:|:----------:|:-----------:|
| Gemini 2.5 |    54.4%     |   64.7%    |   44.1%    |     19%     |
| GPT-5.2    |    61.8%     |   29.4%    |   94.1%    |     22%     |
| Opus 4.5   |    60.3%     |   50.0%    |   70.6%    |     29%     |
| Sonnet 4   |    60.3%     |   32.4%    |   88.2%    |     43%     |

Per-judge voting patterns. GPT and Sonnet show extreme NEG-side bias (94%, 88%); Gemini exhibits the
opposite (65% AFF). Opposing biases partially cancel in panel consensus (55.9%).

</div>

<div class="figure*">

<embed src="fig_judge_bias.pdf" />

</div>

## Tournament V3 Comparison

An earlier tournament (V3, 20 debates) showed no significant difference (trained wins 9/20 = 45%,
$p = 0.82$). V3 had two infrastructure issues that corrupted the signal: (i) panel judge API
failures—Gemini and GPT API keys were expired during parts of the run, leaving some debates scored
only by Claude judges, and (ii) 7 of the 20 debates had at least one `null` speech due to generation
timeouts, creating judge decisions based on incomplete transcripts. V4 resolved both issues: all 68
debates were generated to completion with retries on timeout, and all four panel judges were healthy
throughout the run. The 34-fold difference in statistical power between V3 and V4 (20 vs. 340
judge-debate votes) is the main reason V4 detects the effect that V3 missed; the underlying
trained-model advantage was present in both runs but only became statistically distinguishable at
V4’s sample size.

---

> **from:** `paper/markdown/appendix/appendix_d_failure_modes.md`  →  tex: `paper/appendix/appendix_d_failure_modes.tex`

# Failure Mode Analysis

This appendix documents three failure modes encountered during training with broader implications
for RLAIF pipelines: the *Bicameral Mind Problem* (feedback hallucination in retry generation), the
*Retry Assumption Failure* (inverted preference labels from unconditionally favoring retries), and
the *Group C Regression* (catastrophic divergence from full-LoRA training on a Mixture-of-Experts
base).

## The Bicameral Mind Problem

During iteration 10, we discovered that 35.6% of the model’s thinking sections contained
hallucinated feedback—the model manufactured judge criticism even when no prior feedback existed in
the prompt.

**Quantification (644 samples):**

- 226 contaminated samples from retry attempts

- Only 3 contaminated samples from first-attempt generations

- 28% of “chosen” preference pairs referenced non-existent feedback

**Example (no feedback in prompt):**

> “We are now in a correction phase. The judge’s feedback is severe: the agent failed to conduct any
> searches...” \[No feedback was actually provided\]

**Root cause:** During training, retry attempts included judge feedback in the conversation. The
model learned to associate the debate task with receiving criticism, hallucinating this pattern in
fresh prompts—a form of in-context learning contamination.

**Solution: Proactive self-coaching.** Replace reactive framing (“the judge said you failed...”)
with proactive framing (“when approaching this task, I should verify every citation...”). This
prevents contamination because proactive thoughts don’t require imagining an external critic, and
transfer cleanly to inference.

**General principle:** Training patterns requiring external scaffolding will be hallucinated when
that scaffolding is absent.

## The Retry Assumption Failure

We initially assumed retries were always better than originals, adding a fixed +0.2 score bonus to
all retries. Dual evaluation revealed:

| **Iter** | **Assumed Gap** |  **Actual Gap**  | **Retries Better** |
|:---------|:---------------:|:----------------:|:------------------:|
| 1        |     +0.183      | $-$<!-- -->0.016 |        48%         |
| 2        |     +0.193      | $-$<!-- -->0.007 |        49%         |
| 3        |     +0.191      | $-$<!-- -->0.008 |        48%         |
| 4        |     +0.167      | $-$<!-- -->0.032 |        44%         |

Retry assumption vs. reality. Retries outperform originals only 45% of the time.

Cross-examination retries showed dramatic degradation: CX scores dropped from 0.448 to 0.067–0.233
(60–85% degradation). Hindsight causes loss of natural conversational flow.

**Solution: Dual evaluation.** Score both original and retry independently. Use higher score as
chosen regardless of source. Minimum gap filter ($\geq 0.10$). Skip retry for scores $\geq 0.85$.
Result: 0% inverted preference pairs (vs. 55% before).

## GRPO Regression on MoE Architectures

Group C GRPO training on Qwen3-30B-A3B initially produced a catastrophic regression: mean speech
length dropped from $\sim$<!-- -->400 words to $\sim$<!-- -->100 words within three epochs, and
validation accuracy fell below random (45%). Post-mortem identified three contributing factors.
First, *aggressive LoRA targeting*: we initially adapted all seven linear projections (q/k/v/o +
gate/up/down), producing 3.37B trainable parameters on a 30B base. For a Mixture-of-Experts model,
adapting the expert gating projections (gate/up/down) destabilizes sparse expert routing under
importance-weighted off-policy updates. Second, *wide epsilon clipping*: the PPO-style clip
parameter $\varepsilon$ was set to $0.3$, permitting importance ratios to range over $[0.77, 1.30]$
per step. Combined with a Mixture-of-Experts base, large ratios amplified into large output-space
divergence. Third, *stale logprobs*: because Group B had merged into the canonical model between
Group B logprob capture and Group C training, the reference policy $\pi_{\text{ref}}$ used in
importance ratios was no longer the policy that generated the samples, producing biased gradient
estimates. The combined effect was runaway divergence. The fix
(Appendix [ref:app:grpo_groups]) was attention-only LoRA (53M parameters, a
64$\times$ reduction), tightened $\varepsilon = 0.15$, and mandatory logprob recomputation after
each group merge. These changes together eliminated the regression with no accuracy loss, and we
adopted them as standard practice for all subsequent groups.

---

> **from:** `paper/markdown/appendix/appendix_e_hyperparams.md`  →  tex: `paper/appendix/appendix_e_hyperparams.tex`

# Hyperparameters

| **Parameter**      | **Phase 1 (ORPO)** | **Phase 3 (GRPO)** | **Iter3 Fix**            |
|:-------------------|:-------------------|:-------------------|:-------------------------|
| Base model         | Qwen3-30B-A3B      | Phase 1+2 merged   | Known-good checkpoint    |
| Learning rate      | $5 \times 10^{-7}$ | $5 \times 10^{-7}$ | $1 \times 10^{-5}$       |
| $\beta$ (KL coeff) | 0.1                | 0.1                | 0.1                      |
| Epsilon (clip)     | –                  | –                  | 0.15 (was 0.3)           |
| LoRA rank          | 32                 | 32                 | 32                       |
| LoRA $\alpha$      | 64                 | 64                 | 64                       |
| LoRA targets       | q/k/v/o proj       | q/k/v/o proj       | q/k/v/o only (was all 7) |
| LoRA dropout       | 0.05               | 0.05               | 0.05                     |
| Trainable params   | –                  | –                  | 53M (was 3.37B)          |
| Epochs             | 2                  | 200 steps          | 4                        |
| Effective batch    | –                  | 128                | 64                       |
| DeepSpeed          | ZeRO-3             | ZeRO-3             | ZeRO-3                   |
| Training data      | 15 debates/iter    | 2,830 CX pairs     | 3,274 (cleaned)          |

Training hyperparameters across phases. The Iter3 fix column shows conservative parameters adopted
after the GRPO regression.

## Judge Configuration

| **Dimension**     | **Scale** | **GRPO Weight** | **Focus**                          |
|:------------------|:---------:|:---------------:|:-----------------------------------|
| Tactic Execution  |   0–10    |       1.5       | Strategy alignment, move coherence |
| Opponent Modeling |   0–10    |       1.3       | Adaptation to opponent’s arguments |
| Argumentation     |   0–10    |       1.5       | Logical structure, warrant quality |
| Strategic Impact  |   0–10    |       1.3       | Contribution to debate outcome     |

Judge scoring dimensions with GRPO weights.

Normalized score:
$(\sum w_i \cdot s_i / \sum w_i) - \text{length\_penalty} + \text{novelty\_bonus}$.

---

> **from:** `paper/markdown/appendix/appendix_f_costs.md`  →  tex: `paper/appendix/appendix_f_costs.tex`

# Cost Estimates

| **Component**                             | **Per Unit** |       **Total** | **Notes**                |
|:------------------------------------------|-------------:|----------------:|:-------------------------|
| *Phase 1: Iterative ORPO (12 iterations)* |              |                 |                          |
| Debate generation                         |     \$4/iter |            \$48 | 15 debates/iteration     |
| Judge scoring (Sonnet)                    |     \$2/iter |            \$24 | All speeches + retries   |
| ORPO training                             |     \$8/iter |            \$96 | 8$\times$ A100, 2 epochs |
| *Phase 3: CX Training*                    |              |                 |                          |
| CX data generation                        |            – |            \$15 | 2,830 pairs              |
| GRPO training                             |            – |            \$12 | 200 steps                |
| *Tournament Evaluation*                   |              |                 |                          |
| 68 debates (generation)                   |   \$3/debate |           \$204 | Both models              |
| Panel judging (4 models)                  |   \$5/debate |           \$340 | With bias retries        |
| *Infrastructure*                          |              |                 |                          |
| AWS p4de.24xlarge                         |      \$33/hr |               – | 8$\times$ A100 80GB      |
| vLLM inference                            |            – |               – | Included in compute      |
| **Estimated total**                       |              | **\$750–1,000** |                          |

Approximate cost breakdown. Total project cost is under \$1,000, demonstrating that meaningful RLAIF
for debate is accessible without large annotation budgets.

---

> **from:** `paper/markdown/appendix/appendix_g_debate_examples.md`  →  tex: `paper/appendix/appendix_g_debate_examples.tex`

# Qualitative Debate Examples

This appendix presents excerpted transcripts from the tournament evaluation
(Section [ref:sec:tournament]) that illustrate the side asymmetry finding:
the trained model wins 67.6% of negative-side debates but only 41.2% of affirmative-side debates. We
selected three debates from the 68-debate tournament: (1) the strongest negative win by score
differential, (2) the weakest affirmative loss, and (3) an affirmative win for contrast. All debates
use the IPDA format (AC, AC-CX, NC, NC-CX, 1AR, NR, 2AR).

## Strong Negative Win: “The ends can justify the means”

**Setup.** The trained model debated on the negative side. Final scores: Trained 82.0 vs. Base 37.0
($\Delta = +45.0$), the largest score differential in the tournament.

**NR (Negative Rebuttal) — Trained Model.** This speech exemplifies the reactive strengths that
drive negative-side dominance: systematic refutation of dropped arguments, strategic use of
cross-examination admissions, and clear crystallization of voting issues.

> Thank you. The affirmative has dropped their entire case. Let me be crystal clear about what this
> means for your ballot.
>
> First, the dropped framework. The affirmative’s entire case rested on consequentialism being the
> only coherent moral framework. They claimed it evaluates actions “exclusively by outcomes.” But
> the negative never dropped this argument. In cross examination, the affirmative admitted that
> consequentialism requires counting the negative consequences of means. That is, they agreed that
> if surveillance destroys trust, that matters. But if the means generate their own negative
> consequences, then the ends cannot justify those means. The affirmative’s framework collapses
> under its own weight.
>
> Second, the resolution is empirically false because means must justify themselves. The
> affirmative’s own evidence proves this. Bevan and Hood demonstrated that healthcare providers who
> cut corners to meet vaccination targets eroded public trust and worsened health outcomes. This is
> not a counterexample to our case. This is our case.
>
> Third, the accountability incentives. The affirmative never addressed this. When we only judge by
> results, people who use unethical means to achieve good outcomes are rewarded. \[…\]
>
> Fourth, trust erosion. \[…\] Kavanagh’s research on Truth Decay shows how this uncertainty
> paralyzes society.
>
> Here is the voting issue. The affirmative claimed consequentialism is the only coherent framework.
> They dropped our critique that it treats morality like a mathematical equation. They admitted
> means generating negative consequences undermine the ends. They never explained how their
> framework avoids rewarding unethical behavior. The resolution is false because the means must
> justify themselves. Vote negative.

**Annotation.** The trained model’s NR demonstrates four behaviors characteristic of strong negative
performance: *(i)* explicit tracking of dropped arguments (“the affirmative never addressed this”);
*(ii)* leveraging cross-examination concessions as offensive weapons; *(iii)* turning the opponent’s
evidence against their own position (Bevan and Hood); and *(iv)* clear synthesis into a single
voting narrative. These are fundamentally *reactive* skills—responding to and exploiting the
opponent’s prior speeches—which align with the negative side’s structural advantage of speaking
second.

## Weak Affirmative Loss: “Teacher tenure protections should be eliminated”

**Setup.** The trained model debated on the affirmative side. Final scores: Trained 34.8 vs. Base
74.2 ($\Delta = -39.4$), the largest negative score differential in the tournament.

**AC (Affirmative Constructive) — Trained Model.** The opening speech reveals weak case
construction: the two contentions both rely on the same teacher-shortage evidence but fail to
establish independent warrant for why tenure *causes* the shortage.

> Thank you. \[…\] I stand in firm support of the resolution: Teacher tenure protections should be
> eliminated.
>
> Contention one: Tenure protections prevent timely removal of ineffective educators, directly
> harming student achievement.
>
> The evidence is clear. According to the Economic Policy Institute research, the teacher shortage
> could reach two hundred thousand educators by twenty twenty-five. \[…\] tenure’s lengthy due
> process requirements create twelve to twenty-four month timelines that prevent schools from
> removing consistently ineffective educators. \[…\]
>
> Contention two: Teacher shortages create systemic pressure to retain minimally qualified
> educators, directly compromising educational quality.
>
> The evidence shows almost half of public schools are reporting teacher vacancies. That is
> forty-four percent of schools unable to fill teaching positions. When schools face acute staffing
> crises, they have no choice but to retain minimally qualified educators or leave classrooms
> understaffed.

**Failure pattern: Circular evidence.** Both contentions cite the same EPI teacher-shortage
statistic but conflate a *quantity deficit* (unfilled positions) with a *quality problem* (tenure
protecting ineffective teachers). The opponent’s NC exploits this directly: “the EPI’s 200,000
teacher shortage is a total quantity deficit \[…\] not a turnover rate issue. The Affirmative’s
entire case assumes eliminating tenure will solve this deficit, but their own evidence proves it’s
not about turnover.”

**2AR (Second Affirmative Rebuttal) — Trained Model.** The final speech exhibits the rehashing
pattern identified in Section [ref:sec:side_asymmetry] as a key affirmative failure mode.

> Thank you. This debate comes down to one question: does eliminating teacher tenure protections
> advance student welfare, or does it worsen the crisis?
>
> Voting issue one: the negative’s self-defeating argument only applies to harmful turnover. The
> negative claims eliminating tenure increases turnover. But consider what happens under the current
> system. Frustrated good teachers leave because they cannot be replaced. This creates a vicious
> cycle where schools lose effective educators, then have to hire minimally qualified replacements
> \[…\] Eliminating tenure breaks this cycle.
>
> Voting issue two: the negative’s cost argument misses the real cost. The negative cites twenty
> thousand dollars per turnover event. But that twenty thousand dollars is the cost of KEEPING
> ineffective teachers. \[…\]
>
> Voting issue three: targeted replacement breaks the vicious cycle. \[…\]
>
> Let me give you the real-world example that started this debate. Imagine a fifth-grade classroom
> with an ineffective teacher. Under the current system, removing that teacher could take two years.
> \[…\]

**Annotation: Three failure patterns visible.**

1.  **2AR rehashes 1AR instead of crystallizing.** The 2AR’s “voting issue one” is nearly verbatim
    from the 1AR: both speeches use the identical phrase “frustrated good teachers leave because
    they cannot be replaced … this creates a vicious cycle.” An effective 2AR should synthesize the
    round into two or three decisive voting issues with new framing—not repeat the 1AR’s arguments
    with the same language.

2.  **Failure to address negative contentions.** The opponent’s NC made three distinct arguments:
    (a) the EPI shortage is a quantity deficit not solvable by tenure elimination, (b) removing
    tenure increases turnover per Boyce 2019, and (c) each turnover event costs \$20K and disrupts
    learning continuity. The trained model’s 1AR and 2AR both attempt to “turn” argument (b) but
    never directly refute (a)—the core definitional challenge to the AC’s evidence interpretation.
    The opponent’s NR notes: “they dropped the evidence that tenure prevents removal of ineffective
    teachers.”

3.  **Weak evidence integration.** The AC’s hypothetical fifth-grade classroom example reappears in
    the 2AR with identical language, suggesting the model lacks the ability to generate new
    warranting or reframe evidence under pressure. The trained model recycles its opening
    constructive material rather than developing responsive analysis.

## Affirmative Win (Contrast): “Remote work reduces productivity”

**Setup.** The trained model debated on the affirmative side and won. Final scores: Trained 73.6
vs. Base 48.8 ($\Delta = +24.8$), the largest positive affirmative score differential in the
tournament.

**2AR — Trained Model.** This successful affirmative 2AR illustrates what effective crystallization
looks like, providing a contrast to the tenure debate’s rehashing.

> Thank you. This is the final speech. Let me give you three clear reasons to vote affirmative.
>
> First, the negative’s own words prove our case. In cross examination, the negative said, quote,
> when you send a Slack message, you still have to wait for a response. Then they said, quote,
> waiting fifteen minutes for someone to walk over versus resolving an issue in thirty seconds. This
> is not a technicality. This is the negative admitting that communication delays still occur in
> remote work. \[…\] The negative’s own concession proves the affirmative case.
>
> Second, the negative’s ninety-five percent faster claim is irrelevant. They keep saying delays are
> ninety-five percent faster. But speed of resolution is not the same thing as elimination of delay.
> Waiting thirty seconds is still waiting. That time is still lost.
>
> Third, the negative’s evidence about global talent and commute elimination does not outweigh these
> delays. \[…\]
>
> Here is your choice. Either you believe that waiting for a response reduces productivity, or you
> believe the negative’s semantic claim that remote work increases productivity.

**Annotation.** This 2AR succeeds where the tenure 2AR failed: it uses the opponent’s *specific
cross-examination admissions* (“you still have to wait for a response”) as its primary warrant,
introduces a new analytical frame (speed of resolution $\neq$ elimination of delay), and presents a
clean binary choice for the judge. Notably, these are the same reactive skills that drive the
model’s negative-side dominance. The affirmative wins when the trained model can deploy reactive
argumentation—leveraging opponent concessions—rather than relying solely on proactive case
construction.

## Connection to Side Asymmetry

These examples illuminate the quantitative side asymmetry reported in
Table [ref:tab:side_asymmetry]. The trained model’s core competency is
*reactive argumentation*: tracking dropped arguments, exploiting cross-examination concessions, and
turning opponent evidence. These skills are structurally advantaged on the negative side, where
every speech responds to prior affirmative material. On the affirmative side, the AC must construct
a *proactive* case from scratch, the 1AR must efficiently triage multiple negative attacks, and the
2AR must synthesize the entire debate into crystallized voting issues. When the trained model
defaults to reactive patterns on the affirmative—repeating the same arguments rather than developing
new analysis—it produces the rehashing and weak evidence integration visible in the tenure example.
The affirmative win (remote work) succeeds precisely when the debate structure permits reactive
argumentation even from the affirmative side: a narrow resolution where opponent concessions can
carry the round.

---

> **from:** `paper/markdown/appendix/appendix_h_branching.md`  →  tex: `paper/appendix/appendix_h_branching.tex`

# Branching Implementation Details

The core insight behind our training pipeline is that debate trajectories are not linear sequences
but *trees*: at key decision points, multiple viable continuations exist, and the opponent’s
response may differ depending on which path is taken. We exploit this observation to generate
high-signal counterfactual training pairs.

## BranchDecider Algorithm

At each speech point, the multi-trial generation system produces $k$ candidate speeches (typically
$k{=}4$: two temperature variants and two retry variants). The
<span class="smallcaps">BranchDecider</span> determines whether any pair of candidates would produce
a meaningfully different debate continuation.

#### Divergence score computation.

For each pair of candidate speeches $(s_i, s_j)$, the BranchDecider computes a composite divergence
score across four dimensions:

<div id="tab:divergence_types">

| **Divergence Type** | **Criteria**                                                                            | **Weight** |
|:--------------------|:----------------------------------------------------------------------------------------|:----------:|
| Tactical            | Different macro-tactic or substantially different micro-tactic sequence                 |    0.30    |
| Structural          | Different contention order, dropped vs. addressed arguments, or different voting issues |    0.25    |
| Evidential          | Different evidence cards cited or substantially different warrant construction          |    0.25    |
| Rhetorical          | Different framing, tone, or persuasive strategy (e.g., pathos vs. logos emphasis)       |    0.20    |

Divergence dimensions and their weights in the BranchDecider scoring.

</div>

The composite divergence score is the weighted sum:
$$d(s_i, s_j) = \sum_{t \in \{\text{tac}, \text{str}, \text{evi}, \text{rhe}\}} w_t \cdot d_t(s_i, s_j)$$

where each $d_t \in [0, 1]$ is assessed by the scoring LLM alongside the standard quality
evaluation.

#### Branching conditions.

A branch is created when *both* of the following hold:

1.  **Divergence threshold**: $d(s_i, s_j) \geq 0.15$.

2.  **Viability check**: Both candidates score $\geq 0.65$ on inline quality. This prevents
    branching on a high-quality speech versus a degenerate one, which would produce a trivial
    preference pair.

The key question operationalizing divergence is: *“Would the opponent respond differently to $s_i$
versus $s_j$?”* A high divergence score implies yes, meaning the downstream trajectory will differ
substantively.

#### Branch limits.

Each debate permits at most 4 active branches to bound computational cost. When more than 4 branch
points are identified, the system selects the 4 with highest divergence scores. In practice, most
debates produce 1–2 branches, concentrated at the NC (Negative Constructive) and 1AR (First
Affirmative Rebuttal) speech points where strategic optionality is highest.

## Branch State Tracking

Each branch maintains a `BranchState` record:

<div id="tab:branch_state">

| **Field**          | **Description**                                              |
|:-------------------|:-------------------------------------------------------------|
| `branch_id`        | Unique identifier (format: `debate_id.branch_point.variant`) |
| `parent`           | ID of parent branch (null for the root trajectory)           |
| `child_branches`   | List of child branch IDs created from this branch            |
| `speeches`         | Ordered list of speeches from the branch point onward        |
| `divergence_point` | Speech index where branching occurred                        |
| `divergence_score` | Composite $d(s_i, s_j)$ at the branch point                  |
| `outcome`          | Final debate outcome (win/loss and score) for this branch    |

BranchState record fields.

</div>

Branches share all speeches before the divergence point and maintain independent copies thereafter.
The opponent model generates fresh responses for each branch, ensuring that downstream effects of
the divergent choice are faithfully captured.

## Winner-Shift Detection

The highest-signal training examples arise when different branches produce different debate
outcomes. The winner-shift detection algorithm proceeds as follows:

1.  For each branch pair $(B_a, B_b)$ sharing a parent, compare final outcomes.

2.  A *winner shift* occurs when $\text{outcome}(B_a) \neq \text{outcome}(B_b)$—i.e., the trained
    model wins one branch and loses the other.

3.  For winner-shifted pairs, construct a `CounterfactualInsight`:

<div id="tab:counterfactual_insight">

| **Field**            | **Description**                                                   |
|:---------------------|:------------------------------------------------------------------|
| `losing_choice`      | The speech variant that led to the losing branch                  |
| `winning_choice`     | The speech variant that led to the winning branch                 |
| `impact_explanation` | LLM-generated causal narrative explaining why the choice mattered |
| `confidence`         | Estimated reliability of the causal attribution (0–1)             |
| `score_differential` | $|\text{score}(B_\text{win}) - \text{score}(B_\text{lose})|$      |

CounterfactualInsight structure for winner-shifted branch pairs.

</div>

The `impact_explanation` is generated by prompting the scoring LLM with both complete branch
trajectories and asking it to identify the causal chain from the divergent choice to the outcome
difference. These explanations are preserved for potential use in reasoning distillation.

## Preference Pair Types and Weighting

Branching produces four distinct types of GRPO preference pairs, each weighted according to its
estimated signal quality:

<div id="tab:pair_types">

| **Pair Type** | **GRPO Weight** | **Typical %** | **Construction**                                                                                           |
|:--------------|:---------------:|:-------------:|:-----------------------------------------------------------------------------------------------------------|
| Trial pairs   |   $1.0\times$   |    55–65%     | Best vs. worst among $k$ trials at a single speech point (no branching)                                    |
| Branch pairs  |   $2.0\times$   |    10–15%     | Winner-shifted branch pairs: the winning branch’s speech is chosen, the losing branch’s speech is rejected |
| Golden pairs  |   $1.5\times$   |    15–20%     | Opus-generated reference vs. best model trial; used in SFT pretraining and as high-quality anchors         |
| Retry pairs   |   $1.0\times$   |    10–15%     | Original vs. retry when score gap $\geq 0.10$; higher-scoring variant is chosen regardless of source       |

GRPO preference pair types with weights. Branch pairs receive $2\times$ weight because they carry
outcome-level causal signal rather than speech-level quality signal alone.

</div>

Branch pairs receive elevated weight because they encode a stronger training signal: not merely
“this speech scored higher” but “this choice changed who won the debate.” The $2.0\times$ weight was
selected via ablation (Section [ref:app:grpo_groups]); weights of $1.5\times$ and $3.0\times$
produced lower validation accuracy on held-out debates.

---

> **from:** `paper/markdown/appendix/appendix_i_agentic_judge.md`  →  tex: `paper/appendix/appendix_i_agentic_judge.tex`

# Agentic Judge Architecture

The evaluation system is not a single LLM call but a multi-component *agentic judge* comprising four
dimensional sub-judges, a chronicler for argument state tracking, a forensics module for stage
attribution, and a meta-judge for bias detection and calibration. This appendix provides the full
architecture.

## Dimensional Sub-Judges

Each speech is evaluated by four specialized sub-judges, each with its own rubric and GRPO weight.
Sub-judges operate independently on the same speech and debate context, then their scores are
aggregated.

<div id="tab:sub_judges">

| **Sub-Judge** | **Weight**  | **Scale** | **Rubric Focus**                                                                                  |
|:--------------|:-----------:|:---------:|:--------------------------------------------------------------------------------------------------|
| ArgumentJudge | $1.5\times$ |    0–1    | Claim-warrant linkage, logical validity, argument sophistication, burden of proof allocation      |
| EvidenceJudge | $1.5\times$ |    0–1    | Citation accuracy (verified against source), source credibility, evidence-argument integration    |
| ClashJudge    | $1.3\times$ |    0–1    | Response quality to opponent arguments, identification of dropped arguments, attack effectiveness |
| LanguageJudge | $1.0\times$ |    0–1    | Clarity of expression, persuasive impact, signposting and organization, word economy              |

Dimensional sub-judges with GRPO weights and rubric focus areas. ArgumentJudge and EvidenceJudge
receive higher weight ($1.5\times$) because argument quality and evidence integrity are most
predictive of debate outcomes.

</div>

The composite inline score for speech $s$ is:
$$\text{score}_{\text{inline}}(s) = \frac{\sum_{j} w_j \cdot \text{score}_j(s)}{\sum_{j} w_j}$$

where $j$ indexes the four sub-judges and $w_j$ is the GRPO weight.

## Speech-Specific Primary Dimensions

Beyond the four universal dimensions, each IPDA speech type has a *primary dimension* reflecting its
unique role in the debate structure. The primary dimension receives additional weight in the
composite score for that speech type.

<div id="tab:speech_dimensions">

| **Speech** | **Primary Dimension**     | **Add’l Weight** | **Evaluation Criteria**                                                                                         |
|:-----------|:--------------------------|:----------------:|:----------------------------------------------------------------------------------------------------------------|
| AC         | `prima_facie_case`        |       0.20       | Establishes complete burden structure with independent contentions, clear link chain, and sufficient warranting |
| NC         | `offense_defense_balance` |       0.18       | Strategic time allocation between attacking the AC and building independent negative offense                    |
| 1AR        | `triage_efficiency`       |       0.18       | Prioritized response to NC arguments; addresses highest-impact attacks first within time constraints            |
| NR         | `line_picture_synthesis`  |       0.16       | Extends negative arguments, synthesizes the round into a coherent “big picture” narrative                       |
| 2AR        | `crystallization_cascade` |       0.18       | Reduces the entire debate to 2–3 decisive voting issues with clear impact calculus                              |
| AC_CX_Q    | `case_probe_extraction`   |       0.15       | Negative questions probing the fresh AC for definitional weaknesses and unstated assumptions                    |
| AC_CX_A    | `case_fortification`      |       0.15       | Affirmative answers that protect case structure without conceding strategic ground                              |
| NC_CX_Q    | `offense_limitation`      |       0.15       | Affirmative questions limiting the scope and impact of negative attacks                                         |
| NC_CX_A    | `offense_preservation`    |       0.15       | Negative answers defending attacks while avoiding admissions that weaken offense                                |

Speech-specific primary dimensions in the IPDA format. Constructive speeches (AC, NC) and final
rebuttals (2AR) receive higher additional weight because they have the strongest structural
requirements.

</div>

## Chronicler: Argument State Tracking

The Chronicler module maintains a running record of every argument’s status throughout the debate,
enabling the ClashJudge to accurately identify dropped arguments and the BackpropScorer
(Appendix [ref:app:trajectory]) to attribute outcomes to specific decisions.

Each argument is tracked through six possible states:

<div id="tab:argument_states">

| **State**                               | **Definition**                                                                                    |
|:----------------------------------------|:--------------------------------------------------------------------------------------------------|
| <span class="smallcaps">Standing</span> | Introduced and not yet addressed by the opponent                                                  |
| <span class="smallcaps">Attacked</span> | Directly refuted or challenged by the opponent                                                    |
| <span class="smallcaps">Dropped</span>  | Not addressed in the opponent’s response when it should have been; typically conceded by omission |
| <span class="smallcaps">Extended</span> | Reaffirmed and developed further by the originating side                                          |
| <span class="smallcaps">Conceded</span> | Explicitly acknowledged as valid by the opponent                                                  |
| <span class="smallcaps">Turned</span>   | Opponent has reframed the argument to support their own position                                  |

Argument state taxonomy maintained by the Chronicler.

</div>

The Chronicler processes speeches sequentially, updating its argument ledger after each speech. This
ledger is provided as context to all sub-judges and to the BackpropScorer, ensuring that evaluations
reflect the actual flow of the debate rather than assessing each speech in isolation.

## Forensics: Stage Attribution

When a speech receives a low score, the Forensics module identifies *which pipeline stage* caused
the failure. This decomposition is critical for group-wise GRPO
(Appendix [ref:app:grpo_groups]), as it determines which training group
should receive the penalty signal.

<div id="tab:forensics">

| **Stage**          | **Failure Indicators**                                       | **GRPO Group** |
|:-------------------|:-------------------------------------------------------------|:--------------:|
| Tactic selection   | Wrong strategy for debate state; misread opponent’s position |    Group A     |
| Skeleton building  | Poor contention structure; missing link in argument chain    |    Group B     |
| Evidence selection | Irrelevant evidence; fabricated citations; misquoted sources |    Group B     |
| Speech execution   | Good plan but poor delivery; verbose or unclear prose        |    Group C     |

Forensics stage attribution mapping failures to GRPO training groups.

</div>

The Forensics module produces decomposed rewards: $r_{\text{tactic}}$, $r_{\text{skeleton}}$,
$r_{\text{evidence}}$, and $r_{\text{execution}}$. These are routed to the appropriate training
group, enabling targeted optimization. For example, a speech with excellent argumentation but
fabricated evidence receives a high $r_{\text{execution}}$ but a strongly negative
$r_{\text{evidence}}$, penalizing Group B without degrading Group C’s training signal.

## MetaJudge: Bias Detection and Calibration

LLM judges exhibit systematic biases that, if uncorrected, contaminate training data. The MetaJudge
detects and mitigates six bias types:

<div id="tab:bias_types">

| **Bias Type**                                         | **Description**                                                                 |
|:------------------------------------------------------|:--------------------------------------------------------------------------------|
| <span class="smallcaps">No_Alternative_Penalty</span> | Penalizing an argument without considering the opponent’s alternative           |
| <span class="smallcaps">Extension_Error</span>        | Treating a re-stated argument as a new argument (inflating or deflating scores) |
| <span class="smallcaps">Evidence_Asymmetry</span>     | Applying different evidentiary standards to the two sides                       |
| <span class="smallcaps">Recency_Bias</span>           | Overweighting later speeches relative to earlier ones                           |
| <span class="smallcaps">Verbosity_Bias</span>         | Rewarding longer speeches independent of content quality                        |
| <span class="smallcaps">Side_Bias</span>              | Systematic preference for affirmative or negative regardless of performance     |

Six bias types detected by the MetaJudge.

</div>

#### UniversalBiasTracker.

The MetaJudge maintains a rolling calibration window of the most recent 50 debates. For each judge
model and each bias type, it computes the empirical bias rate and applies score corrections when the
rate exceeds a threshold ($> 0.15$ for most bias types). The calibration window is updated after
each scored debate, enabling the system to adapt to distributional shift as the trained model
improves across iterations.

#### Multi-model retrospective panel.

For tournament evaluation and high-stakes training data curation, a 3-model retrospective panel
(Claude Opus, Gemini, GPT-4) independently evaluates each debate. Points of agreement across all
three models (“agreed key moments”) are flagged as the highest-confidence training signal and
receive elevated weight in GRPO.

## Judge-the-Judge Rubric

To validate judge quality, a meta-evaluation rubric scores each judge decision across five
dimensions:

<div id="tab:judge_rubric">

| **Dimension**        | **Weight** | **Criteria**                                                                            |
|:---------------------|:----------:|:----------------------------------------------------------------------------------------|
| Evidentiary fidelity |    25%     | Does the judge accurately reference what was actually said in speeches?                 |
| Symmetric treatment  |    20%     | Are the same standards applied to both sides?                                           |
| Clash resolution     |    25%     | Does the judge correctly identify who won contested arguments?                          |
| Decision clarity     |    15%     | Is the decision logically derived from the analysis?                                    |
| Technical accuracy   |    15%     | Does the judge correctly apply debate norms (dropped arguments, burden of proof, etc.)? |

Judge-the-judge rubric for meta-evaluation of scoring quality.

</div>

Judges scoring below 0.60 on the meta-rubric have their scores discarded for that debate. In
tournament evaluation, this filtering removed approximately 8% of individual judge decisions,
predominantly due to evidentiary fidelity failures (the judge misattributed or fabricated quotes
from speeches).

---

> **from:** `paper/markdown/appendix/appendix_j_grpo_groups.md`  →  tex: `paper/appendix/appendix_j_grpo_groups.tex`

# GRPO Group Training Details

<div class="figure*">

<embed src="fig_grpo_pipeline.pdf" />

</div>

The debate pipeline produces four heterogeneous call types—tactic selection, skeleton/evidence
construction, speech generation, and cross-examination dialogue—that differ dramatically in output
length, vocabulary, and evaluation criteria. Training a single GRPO objective over all call types
conflates these modalities and produces unstable gradients. We instead partition calls into four
groups (A–D), training each sequentially with group-specific hyperparameters.

## Group Configurations

<div id="tab:grpo_groups">

| **Group** | **Call Types**                                                                    | **Samples** | **Max Tok** | **Batch** | **Epochs** | **Val Acc** |
|:----------|:----------------------------------------------------------------------------------|:------------|------------:|----------:|-----------:|------------:|
| A         | <span class="smallcaps">Tactic_Select</span>                                      | 2,887       |       5,000 |       3–4 |          5 |       81.0% |
| B         | <span class="smallcaps">Skeleton</span> + <span class="smallcaps">Evidence</span> | 4,157       |      16,000 |         3 |          5 |       73.3% |
| C         | <span class="smallcaps">Speech_Generate</span>                                    | 3,274       |      10,500 |         4 |          8 |       72.3% |
| D         | <span class="smallcaps">CX_Dialogue</span>                                        | 5,003       |       7,000 |         4 |          4 |       87.5% |

GRPO group configurations. Max tokens reflects the longest completions in each group. Validation
accuracy is measured on held-out debates from the same iteration. Group D achieves the highest
validation accuracy because CX responses have shorter, more constrained outputs.

</div>

#### Why these groupings.

Group A (tactic selection) has the shortest outputs ($\sim$<!-- -->500–2,000 tokens) and the
clearest reward signal: did the chosen tactic lead to a high-scoring speech? Group B (skeleton +
evidence) is grouped because skeleton structure and evidence selection are tightly coupled—a
skeleton designed around unavailable evidence fails at generation time. Group C (speech generation)
has the longest outputs and the most subjective evaluation, requiring more epochs to converge.
Group D (CX dialogue) is isolated because dialogue has fundamentally different dynamics than
monologue (see Appendix [ref:app:failure_modes] for the retry degradation phenomenon
specific to CX).

## SFT-GRPO Interleaving

Each group follows a two-stage training protocol within each iteration:

1.  **SFT on Opus golden samples.** Claude Opus generates high-quality reference outputs for each
    call type. The model is fine-tuned (SFT) on these samples to establish a strong behavioral
    prior, producing the SFT+ checkpoint.

2.  **GRPO on preference pairs.** The SFT+ model generates $k{=}4$ trial outputs per call (with
    logprob capture). These trials are scored by the agentic judge
    (Appendix [ref:app:agentic_judge]), producing preference pairs. GRPO
    then optimizes the model on these pairs with the group-specific hyperparameters.

3.  **Merge to canonical.** The GRPO LoRA is merged into the canonical base model, which becomes the
    starting point for the next group.

The sequential ordering (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D) is deliberate: tactic
improvements (Group A) propagate to skeleton construction (Group B), which propagates to speech
generation (Group C), and finally dialogue (Group D). Each group trains on top of the improvements
from all preceding groups within the same iteration.

#### Why SFT before GRPO.

GRPO alone can only redistribute probability mass among behaviors the model already exhibits. SFT on
Opus golden samples introduces *new* high-quality behaviors (e.g., more sophisticated argument
structures, better evidence integration) that GRPO can then reinforce through preference
optimization. Without the SFT step, GRPO is limited to choosing among the model’s existing
capabilities.

## Importance Sampling

GRPO requires the log-probability of each response under the current policy. In the offline setting,
responses were generated by a *previous* policy checkpoint. We handle this via importance sampling:

1.  **Logprob capture at generation time.** When the SFT+ model generates trial outputs, per-token
    log-probabilities are recorded alongside the text.

2.  **Importance weight computation.** The GRPO loss uses $\pi_\theta(y|x) / \pi_{\text{ref}}(y|x)$
    ratios, where $\pi_{\text{ref}}$ is the generating policy. Precomputed logprobs from step 1
    serve as $\log \pi_{\text{ref}}$.

3.  **Recomputation after merge.** After each group merge, the canonical model’s policy has shifted.
    For subsequent groups, logprobs from earlier generations become stale. We recompute reference
    logprobs on a random 20% subsample to estimate the KL divergence; if $D_\text{KL} > 0.5$, all
    logprobs for the affected group are recomputed before training.

Stale logprobs were identified as a root cause of the Group C regression described in
Appendix [ref:app:experiment_details]: the importance weights became
extreme, producing unstable gradient updates.

## Advantage Normalization

Standard GRPO normalizes advantages globally across the training batch. This is problematic for
debate because the difficulty of generating a good response depends heavily on the strategic
context: a tactic that works well against one opponent strategy may fail against another.

We normalize advantages within *context triplets*:
$(\text{our\_tactic}, \text{opponent\_tactic}, \text{opponent\_intent})$. For each triplet, the
advantage is: $$A_i = r_i - \bar{r}_{\text{triplet}}$$

where $\bar{r}_{\text{triplet}}$ is the mean reward across all samples sharing the same context
triplet. This ensures that a mediocre response against a strong opponent tactic is not penalized as
harshly as the same response against a weak opponent tactic.

In practice, triplet normalization improved validation accuracy by 3–5 percentage points across all
groups compared to global normalization, with the largest improvement in Group A (tactic selection),
where strategic context has the most direct influence on reward.

## Attention-Only LoRA

During the Group C regression investigation
(Appendix [ref:app:experiment_details]), we discovered that targeting
all seven linear projection modules in the Qwen3-30B-A3B architecture (q_proj, k_proj, v_proj,
o_proj, gate_proj, up_proj, down_proj) produced 3.37 billion trainable parameters. This large
parameter count, combined with stale offline logprobs, caused catastrophic divergence.

Restricting LoRA to attention projections only (q_proj, k_proj, v_proj, o_proj) reduced trainable
parameters to **53 million**—a $\mathbf{64\times}$ reduction. Critically, this produced **no
measurable quality loss**: validation accuracy on Group C was 72.3% with attention-only LoRA versus
72.1% with the full 7-module LoRA (before regression), while completely eliminating the instability.

<div id="tab:lora_comparison">

| **LoRA Config**            | **Params** | **Val Acc** |        **Stable?**         |
|:---------------------------|:----------:|:-----------:|:--------------------------:|
| Full (7 modules)           |   3.37B    |    72.1%    | No (regression at epoch 3) |
| Attention-only (4 modules) |    53M     |    72.3%    |     Yes (all 8 epochs)     |

Comparison of LoRA configurations for Group C GRPO training. Attention-only LoRA achieves equivalent
accuracy with $64\times$ fewer parameters and complete training stability.

</div>

We hypothesize that for Mixture-of-Experts architectures with offline GRPO, the MLP expert layers
(gate_proj, up_proj, down_proj) are particularly sensitive to importance weight noise because each
expert is activated sparsely—small perturbations to expert gating can cascade into large output
changes. Attention-only LoRA avoids this failure mode entirely.

## Per-Group Training Dynamics

#### Group A (Tactic Selection).

Converges fastest (3 epochs to plateau). The primary learning signal is tactic-outcome correlation:
the model learns which macro-tactics succeed against which opponent strategies. Validation accuracy
reaches 81.0%, the highest among speech groups, reflecting the relatively constrained output space.

#### Group B (Skeleton + Evidence).

Requires the longest max token length (16,000) due to evidence card formatting. The evidence
verification penalty (Appendix [ref:app:method_details]) provides a strong shaping signal:
fabrication and hallucination receive $2\times$ GRPO weight, driving the model toward verified
citations early in training.

#### Group C (Speech Generation).

The most challenging group, requiring 8 epochs to converge. Early epochs show improvement in
argument structure; later epochs improve rhetorical quality. The epsilon clipping parameter
($\varepsilon = 0.15$) is critical: values above 0.20 risk the regression described in
Appendix [ref:app:experiment_details].

#### Group D (CX Dialogue).

Achieves the highest validation accuracy (87.5%) but the least improvement over the SFT baseline,
consistent with the finding in Appendix [ref:app:experiment_details] that CX dialogue resists
preference optimization. We attribute this to the interactive nature of dialogue: CX quality depends
as much on the opponent’s responses as on the model’s own outputs, making the reward signal noisier.

## DeepSpeed ZeRO-3 Checkpoint Fix

Training uses DeepSpeed ZeRO-3 across 8 GPUs, which shards model parameters, gradients, and
optimizer states across ranks. A subtle issue arises at checkpoint time: naïvely calling
`model.save_pretrained()` saves only the local shard, producing a corrupted checkpoint. The fix is
to explicitly gather the full state dictionary before saving:

1.  Call `deepspeed.zero.GatheredParameters()` to reconstruct the full parameter tensors on rank 0.

2.  Save the gathered state dict from rank 0 only.

3.  Resume sharded training after the save completes.

This issue is not specific to our pipeline but affects any ZeRO-3 training with LoRA adapters. We
document it here because it caused silent checkpoint corruption during early Group B training runs,
producing models that loaded without error but generated degenerate outputs.

---

> **from:** `paper/markdown/appendix/appendix_k_trajectory.md`  →  tex: `paper/appendix/appendix_k_trajectory.tex`

# Trajectory and Reward Computation

This appendix details the full trajectory capture and reward computation pipeline that connects
debate execution to GRPO training signal.

## DebateTrajectory Structure

Each debate produces a `DebateTrajectory` that records every decision and its outcome:

<div id="tab:trajectory">

| **Field**      | **Description**                                                                                        |
|:---------------|:-------------------------------------------------------------------------------------------------------|
| `speeches`     | Ordered list of all speeches (AC, AC-CX, NC, NC-CX, 1AR, NR, 2AR) with full text and metadata          |
| `aff_turns`    | List of `TurnRecord`s for the affirmative side                                                         |
| `neg_turns`    | List of `TurnRecord`s for the negative side                                                            |
| `judge_scores` | Per-speech scores from all sub-judges (Appendix [ref:app:agentic_judge])                                             |
| `branches`     | List of `BranchState` records (Appendix [ref:app:branching])                                                     |
| `outcome`      | Final debate result: winner, score differential, and judge reasoning                                   |
| `debate_id`    | Unique identifier linking to the resolution and side assignments                                       |

DebateTrajectory top-level fields.

</div>

## TurnRecord

Each turn within the trajectory captures the full decision context:

<div id="tab:turn_record">

| **Field**               | **Description**                                                                                                                                                                 |
|:------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tactic_selection`      | The macro-tactic and micro-tactic sequence chosen for this turn                                                                                                                 |
| `opponent_prediction`   | The model’s predicted opponent response (used for strategic planning)                                                                                                           |
| `opponent_ground_truth` | The actual opponent response observed after the turn                                                                                                                            |
| `novelty_bonus`         | Reward bonus for using a novel tactic combination ($+0.05$ to $+0.15$)                                                                                                          |
| `surprise_bonus`        | Reward bonus when the opponent’s response differs significantly from prediction ($+0.05$ to $+0.10$), indicating the model explored territory not covered by the opponent model |
| `call_records`          | Per-call records for tactic, skeleton, evidence, and speech generation, each with logprobs                                                                                      |

TurnRecord fields capturing per-turn decision context.

</div>

The `opponent_prediction` and `opponent_ground_truth` fields enable the surprise bonus: when the
model’s prediction diverges substantially from reality, it indicates unexplored strategic territory
that may yield high-signal training examples.

## Reward Formula

The per-turn reward combines four components reflecting different aspects of debate quality:

$$r_{\text{combined}} = 0.25 \cdot r_{\text{selection}} + 0.35 \cdot r_{\text{execution}} + 0.25 \cdot r_{\text{quality}} + 0.15 \cdot r_{\text{novelty}}
\label{eq:combined_reward}$$

<div id="tab:reward_components">

| **Component**          | **Weight** | **Source**                                                                                                                          |
|:-----------------------|:----------:|:------------------------------------------------------------------------------------------------------------------------------------|
| $r_{\text{selection}}$ |    0.25    | Tactic appropriateness for the debate state; from Forensics module (Appendix [ref:app:agentic_judge])                                                                          |
| $r_{\text{execution}}$ |    0.35    | Speech quality conditional on the tactic; composite of sub-judge scores                                                             |
| $r_{\text{quality}}$   |    0.25    | Speech-specific primary dimension score (Table [ref:tab:speech_dimensions])                                                                  |
| $r_{\text{novelty}}$   |    0.15    | Novelty bonus $+$ surprise bonus from `TurnRecord`                                                                                  |

Per-turn reward components. Execution receives the highest weight because it reflects the most
direct measure of output quality.

</div>

The final reward incorporates the debate outcome:
$$r_{\text{final}} = 0.7 \cdot r_{\text{combined}} + 0.3 \cdot r_{\text{win}}
\label{eq:final_reward}$$

where $r_{\text{win}} \in \{0, 1\}$ is 1 if the model’s side won the debate and 0 otherwise. The 0.3
weight on the win bonus ensures that outcome signal influences training without overwhelming the
fine-grained per-turn signal. Without the win bonus, the model could learn to produce individually
high-scoring speeches that collectively lose the debate (e.g., strong individual arguments that fail
to cohere into a winning narrative).

## BackpropScorer Algorithm

The BackpropScorer propagates debate-level outcomes back to individual calls, producing causal
attribution of which decisions most influenced the result. This operates in four stages:

#### Stage 1: Outcome analysis.

For each speech in the debate, compute its *outcome contribution* $c_s \in [-1.0, +1.0]$, estimating
how much that speech contributed to the final result. This is assessed by the scoring LLM, which
receives the full debate transcript and is asked: “How much did \[speech\] contribute to \[side\]
winning/losing? Consider what would have changed if this speech had been average rather than
as-delivered.”

#### Stage 2: Branch counterfactual.

For debates with branches (Appendix [ref:app:branching]), identify the divergence point and determine
whether a winner shift occurred. If so, the speeches at the divergence point receive amplified
attribution: their contribution scores are adjusted by the score differential between the winning
and losing branches.

#### Stage 3: Score adjustment.

The final backpropagated score for each call is:
$$r_{\text{backprop}} = r_{\text{inline}} + c_s \cdot 0.2 + b_{\text{critical}} \cdot 0.15 + p_{\text{adj}}
\label{eq:backprop}$$

<div id="tab:backprop_terms">

| **Term**                         | **Description**                                                                                                            |
|:---------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| $r_{\text{inline}}$              | Original inline score from the sub-judges                                                                                  |
| $c_s \cdot 0.2$                  | Outcome contribution scaled by 0.2 to prevent outcome signal from dominating                                               |
| $b_{\text{critical}} \cdot 0.15$ | Critical call boost: $b_{\text{critical}} \in \{0, 1\}$ is 1 if Forensics identifies this call as a pivotal decision point |
| $p_{\text{adj}}$                 | Pivotal adjustment from branch counterfactuals: ranges from $-0.5$ to $+0.5$ for winner-shifted decisions, 0 otherwise     |

BackpropScorer adjustment terms.

</div>

The multiplicative constants (0.2, 0.15) were tuned to keep $r_{\text{backprop}}$ within
approximately $\pm 0.3$ of $r_{\text{inline}}$ for most calls, with larger adjustments reserved for
the small number of genuinely pivotal decisions (typically 2–3 per debate).

#### Stage 4: Reasoning preservation.

The BackpropScorer generates a natural-language explanation for each score adjustment, recording the
causal chain from the call to the debate outcome. These explanations are stored alongside the
training data for potential use in reasoning distillation—training the model to internalize the
judge’s causal reasoning rather than just the scalar reward.

## Group Baselines and Context Triplets

As described in Appendix [ref:app:grpo_groups], GRPO advantages are normalized within
context triplets $(\text{our\_tactic}, \text{opponent\_tactic}, \text{opponent\_intent})$. The
trajectory captures these triplets at each turn, enabling the training pipeline to compute
context-appropriate baselines.

<div id="tab:context_triplets">

| **Triplet Component** | **Source**                                                                                                                                                                 |                **Cardinality** |
|:----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------:|
| Our tactic            | `tactic_selection` from TurnRecord                                                                                                                                         | $\sim$<!-- -->25 macro-tactics |
| Opponent tactic       | Inferred from opponent speech by the judge                                                                                                                                 | $\sim$<!-- -->25 macro-tactics |
| Opponent intent       | Classified as <span class="smallcaps">Attack</span>, <span class="smallcaps">Defend</span>, <span class="smallcaps">Extend</span>, or <span class="smallcaps">Probe</span> |                              4 |

Context triplet components for advantage normalization. The product space is large
($\sim$<!-- -->2,500 triplets) but most debates activate only 15–30 distinct triplets, providing
sufficient samples for meaningful normalization.

</div>

## End-to-End Reward Flow

Figure [ref:fig:reward_flow]
summarizes the complete reward computation pipeline from debate execution to GRPO training signal.

<figure id="fig:reward_flow">
<table>
<tbody>
<tr class="odd">
<td style="text-align: center;"></td>
</tr>
<tr class="even">
<td style="text-align: center;"><strong>Debate Execution</strong></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><code>DebateTrajectory</code> (speeches, turns, branches)</td>
</tr>
<tr class="odd">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><strong>Layer 1: Inline Scoring</strong></td>
</tr>
<tr class="odd">
<td style="text-align: center;">4 sub-judges <span class="math inline">×</span> speech-specific
dimensions <span class="math inline">→</span> <span
class="math inline"><em>r</em><sub>inline</sub></span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><strong>Layer 2: Outcome Backpropagation</strong></td>
</tr>
<tr class="even">
<td style="text-align: center;"><span class="math inline"><em>r</em><sub>inline</sub> + outcome
contribution + critical boost + branch adjustment</span> <span class="math inline">→</span> <span
class="math inline"><em>r</em><sub>backprop</sub></span></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><strong>Layer 3: Meta-Debate Calibration</strong></td>
</tr>
<tr class="odd">
<td style="text-align: center;">3-model panel <span class="math inline">+</span> bias detection
<span class="math inline">+</span> judge-the-judge filtering</td>
</tr>
<tr class="even">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><strong>Reward Assembly</strong></td>
</tr>
<tr class="even">
<td style="text-align: center;"><span
class="math inline"><em>r</em><sub>final</sub> = 0.7 ⋅ <em>r</em><sub>combined</sub> + 0.3 ⋅ <em>r</em><sub>win</sub></span></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><strong>Triplet Normalization</strong></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><span
class="math inline"><em>A</em><sub><em>i</em></sub> = <em>r</em><sub><em>i</em></sub> − <em>r̄</em><sub>(our_tactic,opp_tactic,opp_intent)</sub></span></td>
</tr>
<tr class="even">
<td style="text-align: center;"><span class="math inline">↓</span></td>
</tr>
<tr class="odd">
<td style="text-align: center;"><strong>GRPO Training</strong> (Group A <span
class="math inline">→</span> B <span class="math inline">→</span> C <span
class="math inline">→</span> D)</td>
</tr>
<tr class="even">
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>
<figcaption>End-to-end reward flow from debate execution to GRPO training. Each layer adds
finer-grained signal: inline scoring evaluates individual speeches, backpropagation attributes
outcomes to decisions, and meta-debate calibration removes judge bias.</figcaption>
</figure>

---

> **from:** `paper/markdown/appendix/appendix_l_pipeline.md`  →  tex: `paper/appendix/appendix_l_pipeline.tex`

# Debate Generation Pipeline Details

This appendix expands
Section [ref:sec:pipeline].
The pipeline is shared identically between baseline and experimental runs; all quality differences
reported in the main body therefore come from the speech generation model and training procedure,
not from asymmetric preparation.

## Belief Tree Structure

From a resolution $R$, the pipeline constructs a typed belief tree in three passes.

#### Values.

A DSPy <span class="smallcaps">ValueExtractor</span> module generates 4 topic-specific values, 2 per
side, phrased as terminal goods the side should be understood to defend (e.g., *economic mobility*,
*institutional trust*). Values are the roots of the belief tree.

#### Beliefs.

A <span class="smallcaps">BeliefGenerator</span> expands each value into 2 child beliefs per side,
then refines each to depth-2, yielding approximately 32 beliefs total and 16 arguments per side.
Each belief $b$ carries a Bayesian credence $c(b)\in[0,1]$; the prior is set by the generator and is
later updated as posteriors conditioned on speeches delivered.

#### Arguments.

Leaf beliefs are instantiated as typed arguments drawn from standard debate theory:
<span class="smallcaps">uniqueness</span>, <span class="smallcaps">link</span>,
<span class="smallcaps">impact</span>, <span class="smallcaps">solvency</span>, and
<span class="smallcaps">turn</span>. Typing is important: it gives the downstream speech stages
structured slots (e.g., an impact argument must identify magnitude, timeframe, probability), and it
allows the hierarchical reward (Section [ref:sec:reward_hierarchy]) to reason about the debate at the
level of argument roles rather than raw sentences.

## Research Pipeline: v1 vs. v2

#### v1 (9 LLM calls per hop).

The original research agent made separate LLM calls for: query formulation, query rewriting,
relevance filtering, per-document summarization, per-sentence judgement, selection ranking, card
tagging, citation extraction, and hop termination. Typical claims took 3–4 hops, burning
$\sim$<!-- -->30 calls per claim and dominating preparation cost.

#### v2 (2 LLM calls per hop, consolidated).

The consolidated loop per claim is:

1.  **Query generation (LLM call 1):** A single structured call emits $k$ retrieval queries plus
    termination heuristics.

2.  **Parallel retrieval:** Weaviate (dense) and Tavily (web) run in parallel on each query.

3.  **Deterministic processing:** Text is cleaned, chunked into sentences, and scored with hybrid
    $s = 0.7\cdot \cos(\mathbf{q},\mathbf{s}) + 0.3\cdot\mathrm{BM25}(q,s)$. Top sentences are
    expanded into windows to preserve local context.

4.  **Selection (LLM call 2):** A single structured call consumes the candidate windows and emits
    the final evidence card via Pydantic validation, including bolded selections and sentence IDs.

Most claims terminate after one hop. Total calls per claim drop from $\sim$<!-- -->30 to
$\sim$<!-- -->2–4, a 10$\times$ reduction that is what makes the downstream branching tree
(Section [ref:sec:branching]) economically feasible.

## Evidence Card Schema

Each card is a Pydantic record with the following fields:

- `tag` — one-line argumentative claim.

- `cite`, `fullcite` — short and full citations.

- `full_text` — the complete retrieved passage.

- `card` — the passage with **bolded** sentences indicating selected material.

- `selected_texts` — list of selected sentences as strings.

- `selected_sentence_ids` — indices into `full_text`, the *only* handle the speech generator can
  cite.

- `window_ranges` — windows around each selection used for context.

- `source_url` — retrieval source for audit.

- `relevance_score` — retrieval score used by sorting.

Because downstream speech generation cites by `selected_sentence_id` only, the quotation text is
mechanically assembled from `full_text` and cannot be fabricated by the model. This is the
structural property that makes evidence verification in
Section [ref:sec:reward_hierarchy] a sentence-ID check rather than a
natural-language fidelity judgment.

## Perspective Building

Given the completed belief tree, a <span class="smallcaps">PerspectiveBuilder</span> compiles
side-specific prompt contexts:

- **Constructives** receive a pruned depth-1 view: 2 of the 4 root beliefs for the side, chosen to
  cover complementary ground. This forces the constructive speech to commit to a narrow thesis
  rather than diffuse across all available arguments.

- **Rebuttals** receive the full sub-belief tree in SEAM form (Setup, Evidence, Analysis, Move),
  which aligns naturally with rebuttal block structure in competitive debate.

- **CX** receives the opponent’s most recent constructive along with attackable beliefs.

Different branches of the debate tree (Section [ref:sec:branching]) are seeded with different D1 belief
combinations, producing natural debate diversity without any hand-written prompts or per-topic
tuning.

## Why Automation Matters

#### Reproducibility.

Every piece of training data is reproducible from the original resolution plus the research index
snapshot: there is no human-curated brief, no pre-written argument, no case file. This matters for
scientific validity; it also matters for operational robustness when we replay or audit training
runs.

#### Scale.

The pipeline runs end-to-end on a resolution in minutes, making tournament generation (68 debates)
and training-scale generation (thousands of debates) feasible on a small budget ($\sim$\$750–1,000
total;
Appendix [ref:app:costs]).

#### Baseline/experimental comparability.

The same pipeline produces the inputs for both the base Qwen3-30B-A3B and all trained checkpoints. A
difference in downstream win rate therefore cannot be attributed to a richer prep stage, a better
research index, or stronger evidence — the substrate is identical, so the delta isolates the
generation model. This is a property we rely on for the tournament analysis in
Section [ref:sec:analysis].

#### Ablation surface.

Because the pipeline is structured rather than monolithic, components can be ablated independently:
belief tree depth, research-hop limits, SEAM structure, and the four-stage decomposition itself.
Each is a natural axis of ablation and a natural training target, independent of the specific model
being trained.

---

