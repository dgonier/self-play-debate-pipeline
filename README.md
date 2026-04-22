# Self-Play Debate Pipeline

Companion repository for the paper:

> **Can LLMs Improve at Debate Through Self-Play? A Pipeline and RL System to Gamify Competitive Debate with Branching and Hierarchical Rewards**
> *NeurIPS 2026 submission*

This repository contains the LaTeX source for the paper and the experimental
tournament results that support its claims. The training pipeline itself is
proprietary and is described in the paper rather than released here — see
[Reproducibility](#reproducibility) below.

---

## Contents

```
paper/
    main.tex                # NeurIPS 2026 paper source (Overleaf-ready)
    neurips_approx.sty      # Style file
    references.bib          # Bibliography
    sections/               # Body sections (introduction ... conclusion)
    appendix/               # Appendices A–L
    figures/                # Rendered figures (PDF/PNG/SVG)
    diagrams/               # Architecture diagrams (d2 source + renders)

results/
    tournament_v3/          # Tournament V3 experimental data
        tournament_v3_results.json          # Per-debate outcomes
        tournament_v3_report.md             # Human-readable report
        tournament_v3_final_analysis.md     # Statistical analysis
        tournament_v3_audit.md              # Run audit
        debiased_analysis.md                # Judge-bias correction
        panel_rejudge_v3_fast.json          # Panel re-judgement
        v3_t{1..12}_trained_{aff,neg}.json       # Per-debate summaries
        v3_t{1..12}_trained_{aff,neg}_full.json  # Full trajectories
                                                  # (speeches, belief trees,
                                                  #  call records, scores)
        topic5_rerun/                       # Topic 5 rerun + panel judgements
        topic_bias_probe.json               # Topic-order bias probe
```

---

## The Paper

`paper/main.tex` is the top-level LaTeX file. It is self-contained and builds
under a standard TeX Live / Overleaf environment using the NeurIPS 2026 style
(`neurips_approx.sty`). All referenced figures are checked in under
`paper/figures/`, so the project should compile out of the box.

**To build locally:**
```bash
cd paper && latexmk -pdf main.tex
```

**To use in Overleaf:** upload the contents of `paper/` as a new project.

---

## The Experiments

### Setup
- **Trained model**: Qwen3-30B-A3B fine-tuned with SFT then GRPO on
  DebaterHub's debate pipeline.
- **Base model**: `Qwen/Qwen3-30B-A3B-Thinking-2507` (unmodified).
- **Format**: International Public Debate Association (IPDA), head-to-head.
- **Tournament V3**: 12 resolutions × 2 sides = 24 debates (23 complete).

### Headline results (pipeline judge, N=23)

| Metric | Trained vs. Base |
|---|---|
| Win rate | 30% vs. 70% |
| Mean score Δ | −2.1 (SD=16.9) |
| Cohen's d | −0.126 (negligible) |
| Paired t-test p | 0.551 |
| Binomial p | 0.093 |

### Headline results (panel of LLM judges, N=23)

| Metric | Trained vs. Base |
|---|---|
| Win rate | 44% vs. 56% |

**Key finding**: the aggregate win-rate gap is not significant under either
judge, but **side-conditional win rates diverge sharply** (trained-as-NEG: 55%,
trained-as-AFF: 8%), motivating the discussion of judge bias and side
asymmetry in the paper. Analysis files in `results/tournament_v3/` include the
per-debate full trajectories (`*_full.json`) with all 33 call records per
debate, belief trees, branching decisions, and individual speech scores.

### File formats
Summary JSONs (`v3_tN_trained_{aff,neg}.json`) contain the high-level
outcome and the four speeches. Full JSONs (`*_full.json`) contain the entire
debate trajectory: the Bayesian belief tree, every LLM call record with its
scored output, and the final judge breakdown. See the paper's appendix C
(tournament details) and appendix K (trajectory schema) for a full
specification.

---

## Reproducibility

The debate generation pipeline, branching search procedure, hierarchical
reward system, and RL training code described in the paper are **not released
publicly**. DebaterHub is a commercial product; releasing the pipeline would
expose production-grade prompts, orchestration, and training infrastructure.

The paper is written to be self-contained:

- **Section 3 (Method)** specifies the pipeline: call decomposition, belief-tree
  preparation, research loop, evidence selection, and generation stages.
- **Section 4 (Experiments)** specifies the tournament protocol and training
  regime.
- **Appendix E** lists all hyperparameters.
- **Appendix A, L** give method and pipeline details.
- **Appendix H** specifies the branching search algorithm.
- **Appendix J** specifies the GRPO group construction and reward shaping.

For researchers who need access to the pipeline for reproduction, benchmarking,
or collaboration, DebaterHub offers contractual API access. Contact:

**dgonier@debaterhub.com**

### Public SDKs

If you hold a DebaterHub contract, two thin client reference implementations
are public and can be used to invoke the pipeline via API:

- [**debate-fastapi-reference**](https://github.com/dgonier/debate-fastapi-reference)
  — FastAPI reference app (requires `.env` with issued credentials).

---

## Citation

```bibtex
@inproceedings{selfplay-debate-2026,
  title   = {Can LLMs Improve at Debate Through Self-Play?
             A Pipeline and RL System to Gamify Competitive Debate
             with Branching and Hierarchical Rewards},
  author  = {Anonymous Authors},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year    = {2026}
}
```

## License

See [LICENSE](./LICENSE). Results in `results/` are CC BY 4.0. The paper
source in `paper/` is for peer review and non-commercial academic use. The
training pipeline is proprietary.

## Contact

dgonier@debaterhub.com
