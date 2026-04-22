# Cost Estimates

| **Component**                             | **Per Unit** |       **Total** | **Notes**                |
|:------------------------------------------|-------------:|----------------:|:-------------------------|
| *Phase 1: Iterative ORPO (12 iterations)* |              |                 |                          |
| Debate generation                         |     \$4/iter |            \$48 | 15 debates/iteration     |
| Judge scoring (Sonnet)                    |     \$2/iter |            \$24 | All speeches + retries   |
| ORPO training                             |     \$8/iter |            \$96 | 8$\times$ A100, 2 epochs |
| *Phase 3: CX Training*                    |              |                 |                          |
| CX data generation                        |            – |            \$15 | 2,830 pairs              |
| GRPO training                             |            – |            \$12 | 200 steps                |
| *Tournament Evaluation*                   |              |                 |                          |
| 68 debates (generation)                   |   \$3/debate |           \$204 | Both models              |
| Panel judging (4 models)                  |   \$5/debate |           \$340 | With bias retries        |
| *Infrastructure*                          |              |                 |                          |
| AWS p4de.24xlarge                         |      \$33/hr |               – | 8$\times$ A100 80GB      |
| vLLM inference                            |            – |               – | Included in compute      |
| **Estimated total**                       |              | **\$750–1,000** |                          |

Approximate cost breakdown. Total project cost is under \$1,000, demonstrating that meaningful RLAIF
for debate is accessible without large annotation budgets.
