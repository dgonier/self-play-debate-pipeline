# Hyperparameters

| **Parameter**      | **Phase 1 (ORPO)** | **Phase 3 (GRPO)** | **Iter3 Fix**            |
|:-------------------|:-------------------|:-------------------|:-------------------------|
| Base model         | Qwen3-30B-A3B      | Phase 1+2 merged   | Known-good checkpoint    |
| Learning rate      | $5 \times 10^{-7}$ | $5 \times 10^{-7}$ | $1 \times 10^{-5}$       |
| $\beta$ (KL coeff) | 0.1                | 0.1                | 0.1                      |
| Epsilon (clip)     | –                  | –                  | 0.15 (was 0.3)           |
| LoRA rank          | 32                 | 32                 | 32                       |
| LoRA $\alpha$      | 64                 | 64                 | 64                       |
| LoRA targets       | q/k/v/o proj       | q/k/v/o proj       | q/k/v/o only (was all 7) |
| LoRA dropout       | 0.05               | 0.05               | 0.05                     |
| Trainable params   | –                  | –                  | 53M (was 3.37B)          |
| Epochs             | 2                  | 200 steps          | 4                        |
| Effective batch    | –                  | 128                | 64                       |
| DeepSpeed          | ZeRO-3             | ZeRO-3             | ZeRO-3                   |
| Training data      | 15 debates/iter    | 2,830 CX pairs     | 3,274 (cleaned)          |

Training hyperparameters across phases. The Iter3 fix column shows conservative parameters adopted
after the GRPO regression.

## Judge Configuration

| **Dimension**     | **Scale** | **GRPO Weight** | **Focus**                          |
|:------------------|:---------:|:---------------:|:-----------------------------------|
| Tactic Execution  |   0–10    |       1.5       | Strategy alignment, move coherence |
| Opponent Modeling |   0–10    |       1.3       | Adaptation to opponent’s arguments |
| Argumentation     |   0–10    |       1.5       | Logical structure, warrant quality |
| Strategic Impact  |   0–10    |       1.3       | Contribution to debate outcome     |

Judge scoring dimensions with GRPO weights.

Normalized score:
$(\sum w_i \cdot s_i / \sum w_i) - \text{length\_penalty} + \text{novelty\_bonus}$.
