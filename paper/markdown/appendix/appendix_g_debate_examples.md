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
