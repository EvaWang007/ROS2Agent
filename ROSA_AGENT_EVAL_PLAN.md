# ROSA Agent Evaluation Plan (LangSmith Workflow)

## Objective
This plan defines a practical, reproducible evaluation workflow for the current ROSA agent project using LangSmith (official workflow) plus ROS-specific engineering checks.

Primary goals:

1. Quantify current ROSA agent capability.
2. Compare `lexical memory` vs `hybrid memory`.
3. Produce a reusable evaluation report for engineering review and resume/interview evidence.

---

## Scope
This evaluation targets three layers:

1. End-to-end answer quality.
2. Tool-calling trajectory quality.
3. Long-term memory effectiveness.

---

## Phase 0: Environment & Experiment Baseline

### Tasks

1. Configure LangSmith:
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_TRACING=true`
   - `LANGSMITH_PROJECT=rosa-agent-evals`
2. Freeze experiment settings:
   - model name
   - temperature
   - ROS scene
   - memory path
   - top_k
3. Record versions and runtime assumptions.

### Deliverable

- `eval/config.md`

---

## Phase 1: Build Evaluation Dataset

### Step 1 (Bootstrap)

1. Create one sample and run a full eval loop end-to-end.
2. Validate data format and evaluator integration.

### Step 2 (Scale)

Expand to ~50 samples with four classes:

1. Symbol-precise questions (e.g., `/cmd_vel`, `/tf`).
2. Natural-language diagnosis questions.
3. Mixed questions (language + ROS symbols).
4. Adversarial questions (attempt to skip tool observation).

### Per-sample fields

1. `input.query`
2. `reference.expected_answer`
3. `reference.must_include`
4. `reference.forbidden_claims`
5. `reference.expected_tools` (optional)
6. `metadata.scene_id`, `metadata.robot_id`, `metadata.domain`

### Deliverables

- `eval/datasets/rosa_eval_v1.jsonl`
- LangSmith dataset with the same content

---

## Phase 2: Define Evaluators

Use mixed evaluators (LLM-as-judge + rule-based).

### Evaluators

1. `AnswerCorrectness` (LLM judge)
   - Does the answer resolve the query?
   - Is it operationally useful?
2. `MustInclude` (rule)
   - Required symbols/entities exist in output.
3. `NoHallucination` (rule + optional LLM check)
   - Prevent fabricated nodes/topics/services.
4. `TrajectoryCompliance` (rule)
   - Check observation-first pattern (`list/info` before conclusions).
5. `MemoryUtility` (rule)
   - Memory hit usefulness.
   - Wrong memory injection rate.

### Deliverable

- `eval/evaluators.py`

---

## Phase 3: Run Baseline (Lexical)

### Tasks

1. Set `ROSA_MEMORY_MODE=lexical`.
2. Run full dataset with fixed model/config.
3. Export run metrics.

### Deliverables

- LangSmith experiment: `rosa_eval_lexical_v1`
- `eval/results/lexical_v1.csv`

---

## Phase 4: Run Experiment (Hybrid)

### Tasks

1. Set `ROSA_MEMORY_MODE=hybrid`.
2. Keep all other variables unchanged.
3. Run the same dataset.

### Deliverables

- LangSmith experiment: `rosa_eval_hybrid_v1`
- `eval/results/hybrid_v1.csv`

---

## Phase 5: A/B Analysis

Compare lexical vs hybrid on:

1. Final correctness
2. Must-include hit rate
3. Hallucination rate
4. Trajectory compliance
5. Memory hit rate / wrong memory rate
6. Average latency / token cost

### Deliverables

- `eval/analysis/ab_compare.ipynb` (or `ab_compare.py`)
- `eval/results/ab_summary.json`

---

## Phase 6: Final Evaluation Report

Recommended report structure:

1. Environment and setup
2. Dataset composition
3. Evaluator definitions
4. A/B metrics table
5. Success/failure case studies
6. Conclusions and next optimization actions

### Deliverables

- `eval/reports/ROSA_Agent_Eval_Report_v1.md`
- `eval/reports/ROSA_Agent_Eval_OnePager.md`

---

## Practical Notes for This Project

1. Reuse existing trace signals and memory score breakdown fields:
   - `_score_lex`, `_score_vec`, `_score_meta`, `_score_final`
2. Prioritize proving hybrid value with two constraints:
   - Better natural-language recall/accuracy
   - No regression on symbol-precision tasks
3. Keep iteration order:
   - First run reliably
   - Then compare reliably
   - Then optimize with confidence

---

## Success Criteria

This evaluation is considered complete when:

1. Dataset + evaluators + run scripts are reproducible.
2. Lexical and hybrid A/B runs are available in LangSmith and exported.
3. A written report exists with quantified conclusions and actionable next steps.

