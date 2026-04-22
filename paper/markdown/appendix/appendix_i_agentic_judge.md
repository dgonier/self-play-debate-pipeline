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
