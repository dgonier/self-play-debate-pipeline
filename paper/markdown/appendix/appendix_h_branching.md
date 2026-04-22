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
