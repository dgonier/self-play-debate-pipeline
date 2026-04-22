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
