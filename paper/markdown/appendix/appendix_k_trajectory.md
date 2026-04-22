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
