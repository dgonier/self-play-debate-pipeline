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
