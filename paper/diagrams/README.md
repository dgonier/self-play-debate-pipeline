# Debate Pipeline Diagrams

These D2 diagrams document the complete debate system architecture. Use with the Kroki backend (`deploy/kroki`) to render SVGs.

## Diagram Hierarchy

```
00_overview.d2
├── 01_belief_prep_pipeline.d2   (Belief Prep phase)
├── 02_speech_generation_stages.d2   (4-Stage Speech Pipeline)
├── 03_flow_study.d2   (Debate State Analysis)
├── 04_full_debate_orchestration.d2   (LangGraph End-to-End)
├── 05_judge_system.d2   (Agentic Judge)
├── 06_belief_debate_loop.d2   (Bidirectional Integration)
└── 07_research_pipeline.d2   (V2 Multi-hop Tavily)
```

## Rendering Diagrams

### Using Kroki (Local)

```bash
# Start Kroki backend
cd deploy/kroki && modal serve app.py

# Render a diagram
curl -X POST "http://localhost:8000/" \
  -H "Content-Type: text/plain" \
  --data-binary @00_overview.d2 \
  -o 00_overview.svg
```

### Using Kroki (Public)

```bash
# Render via public kroki.io
curl -X POST "https://kroki.io/d2/svg" \
  -H "Content-Type: text/plain" \
  --data-binary @00_overview.d2 \
  -o 00_overview.svg
```

### Using Python

```python
from packages.diagrams import get_kroki_client
import asyncio

async def render_all():
    client = get_kroki_client()

    diagrams = [
        "00_overview.d2",
        "01_belief_prep_pipeline.d2",
        "02_speech_generation_stages.d2",
        "03_flow_study.d2",
        "04_full_debate_orchestration.d2",
        "05_judge_system.d2",
        "06_belief_debate_loop.d2",
        "07_research_pipeline.d2",
    ]

    for d2_file in diagrams:
        with open(d2_file) as f:
            source = f.read()

        svg = await client.render_d2(source)

        svg_file = d2_file.replace(".d2", ".svg")
        with open(svg_file, "wb") as f:
            f.write(svg)

        print(f"Rendered: {svg_file}")

asyncio.run(render_all())
```

## Diagram Descriptions

### 00_overview.d2 - System Overview
High-level architecture showing the four main phases:
1. **Belief Prep** - Topic → BeliefTree generation
2. **Debate Execution** - 7 speeches + CX via LangGraph
3. **Judge Evaluation** - Multi-dimensional agentic judging
4. **Belief Update** - Bayesian credence updates

### 01_belief_prep_pipeline.d2 - Belief Prep Pipeline
Detailed breakdown of belief tree generation:
- Value extraction (DSPy)
- Belief generation (AFF/NEG sides)
- Recursive refinement (D1 → D2+)
- V2 Research integration
- Argument generation (Claim-Warrant-Impact)

### 02_speech_generation_stages.d2 - 4-Stage Speech Pipeline
The core speech generation process:
1. **Tactic Selection** - Choose strategy from playbook
2. **Skeleton Building** - Structure arguments with belief grounding
3. **Evidence Selection** - Two-phase article + sentence selection
4. **Speech Generation** - Execute skeleton with evidence

### 03_flow_study.d2 - Flow Study (Debate State Analysis)
Analyzes debate state before rebuttal speeches:
- Argument inventory (standing/attacked/dropped)
- Clash point identification
- Voting issue crystallization
- Line-by-line priority generation

### 04_full_debate_orchestration.d2 - Full Debate (LangGraph)
End-to-end IPDA debate execution:
- AC → AC-CX → NC → NC-CX → 1AR → NR → 2AR
- FlowStudy integration for rebuttals
- CX strategy and exchanges
- Judge collection

### 05_judge_system.d2 - Agentic Judge System
Multi-layer judge architecture:
1. **Dimensional Judges** - Parallel evaluation (argument, evidence, clash, language, CX)
2. **Chronicler** - Memory and argument tracking
3. **Pipeline Forensics** - Failure attribution (tactic/skeleton/evidence/execution)
4. **Meta-Judge** - Bias detection and calibration

### 06_belief_debate_loop.d2 - Belief ↔ Debate Integration
Bidirectional flow:
- **Belief → Debate**: Perspective object feeds skeleton builder
- **Debate → Belief**: Outcome updates credences via Bayesian conditionalization
- Convergence checking for iterative debate loop

### 07_research_pipeline.d2 - V2 Research Pipeline
Consolidated multi-hop research:
- 2-3 LLM calls per hop (vs 9 in old pipeline)
- Auto steps: clean, chunk, score, rank
- LLM steps: generate queries, select sentences
- Decision loop for multi-hop research

## Style Guide

All diagrams use **Presentation style**:
- Bold colors with high contrast
- Consistent color coding:
  - **Green** (#C6F6D5) - AFF / success / output
  - **Red** (#FED7D7) - NEG / input / errors
  - **Blue** (#EBF8FF) - Processing / pipeline
  - **Purple** (#FAF5FF) - Judge / evaluation
  - **Orange** (#FEEBC8) - CX / research
  - **Teal** (#E6FFFA) - Beliefs / persistence
  - **Yellow** (#FEF3C7) - Updates / bayesian
- Stroke widths: 2-3 for main components
- Dashed lines for optional/feedback paths

## Related Code

| Diagram | Primary Code Location |
|---------|----------------------|
| 00_overview | (architecture overview) |
| 01_belief_prep | `packages/cognitive/beliefs/refiner.py` |
| 02_speech_gen | `packages/debate/pipeline/unified_pipeline.py` |
| 03_flow_study | `packages/debate/flow/flow_study.py` |
| 04_orchestration | `packages/debate/langgraph_orchestrator/` |
| 05_judge | `packages/debate/judge/` |
| 06_belief_loop | `packages/cognitive/beliefs/debate_integration.py` |
| 07_research | `packages/debate/research/v2/pipeline.py` |
