# Prose-only markdown mirror

Auto-generated from the LaTeX source in `paper/sections/` and `paper/appendix/`.
**Not the source of truth** — the `.tex` files are. This directory exists so
prose edits can be drafted and reviewed in markdown-friendly PRs, then ported
back to LaTeX after approval.

## Reading order

### Body
1. [Introduction](sections/01_introduction.md)
2. [Related Work](sections/02_related_work.md)
3. [Method](sections/03_method.md)
4. [Experiments](sections/04_experiments.md)
5. [Analysis](sections/05_analysis.md)
6. [Conclusion](sections/06_conclusion.md)

### Appendices
- [A. Method details](appendix/appendix_a_method_details.md)
- [B. Experiment details](appendix/appendix_b_experiment_details.md)
- [C. Tournament details](appendix/appendix_c_tournament_details.md)
- [D. Failure modes](appendix/appendix_d_failure_modes.md)
- [E. Hyperparameters](appendix/appendix_e_hyperparams.md)
- [F. Costs](appendix/appendix_f_costs.md)
- [G. Debate examples](appendix/appendix_g_debate_examples.md)
- [H. Branching](appendix/appendix_h_branching.md)
- [I. Agentic judge](appendix/appendix_i_agentic_judge.md)
- [J. GRPO groups](appendix/appendix_j_grpo_groups.md)
- [K. Trajectory](appendix/appendix_k_trajectory.md)
- [L. Pipeline](appendix/appendix_l_pipeline.md)

## What's preserved, what's not

**Preserved:**
- All prose and structural headings
- Inline math (`$...$`) and display math (`$$...$$`) — mostly intact, verify on port-back
- Emphasis, lists, code spans
- Citations as `[cite:key]` markers (do NOT delete these — they mark where
  `\cite{key}` goes in the LaTeX)
- Cross-references as `[ref:label]` markers (same — these mark `\ref{label}`)

**Stripped:**
- Figures, tables, algorithms, theorem environments
- Captions (these live in the `.tex` only)
- Custom LaTeX macros, `\input`, label/ref targets

## Editing workflow

1. Branch: `git checkout -b edits/<topic>`
2. Edit the relevant `.md` file(s). Keep lines wrapped at ~100 chars for
   readable diffs.
3. Do not touch `[cite:...]` or `[ref:...]` markers unless you intend to
   change the citation/reference itself.
4. Commit, push, open a PR.
5. After PR approval, the prose diff will be ported manually into the
   matching `.tex` file in a follow-up commit on `main`.
