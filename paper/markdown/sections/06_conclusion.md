# Conclusion

We presented a system that treats structured multi-turn debate as search: an automated prep
pipeline, branching counterfactual credit assignment, a three-layer hierarchical reward over
${\sim}33$ calls, and group-wise offline GRPO. The trained model wins 58.2% of judge votes in a
68-debate tournament ($p = 0.034$, GEE). Four contributions generalize: (1) the prep pipeline
demonstrates that structured generation can be fully automated without human curation, enabling
rigorous baseline/experimental comparisons; (2) branching gives causal signal from winner-shifts;
(3) hierarchical reward enables fine-grained attribution; (4) modality-grouped training resolves
cross-modality interference. A structural side asymmetry (67.6% NEG vs. 41.2% AFF) suggests reactive
argumentation is more amenable to preference optimization than generative case construction. Total
cost: \$750–1,000
(Appendix [ref:app:costs]).
Future work: deeper branching, human expert evaluation, and targeted affirmative-side distillation.
Debate training carries dual-use risk, and the asymmetric role effect we document underscores the
need for per-role evaluation. Code and corpora: `[anonymized]`.
