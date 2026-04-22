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
