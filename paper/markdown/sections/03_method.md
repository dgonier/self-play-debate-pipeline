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
