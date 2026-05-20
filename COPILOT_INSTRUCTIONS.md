# COPILOT_INSTRUCTIONS

## Required files and layering
- `app/main.py`
- `policy/gate.py`
- `observability/audit.py`

## Step-by-step implementation rules
1. Generate a `run_id` (UUID) at the start of every request.
2. Pass `run_id` to **all** logging calls.
3. Use structured logging (dict/JSON) with no hidden logs.
4. Keep policy non-blocking and non-mutating:
   - never block execution
   - never modify input
   - only generate policy signals/warnings
5. Treat warnings as soft warnings:
   - do not interrupt execution
   - log them when present
   - do not change system output
6. Keep core processing independent:
   - no dependency on classification
   - no conditional branching from warnings
7. Main flow mental model:
   - Policy observes
   - Observability records
   - Core executes
8. Keep a controller loop around execution:
   - Planner → Executor → Evaluator → Controller → back to context
   - detect stagnation (same plan + same output)
   - inject movement via direction shift/state mutation when stagnant

## Non-negotiable constraints
Copilot MUST NOT:
- block input
- modify input
- inject enforcement logic
- skip `run_id` in logs
- couple policy with processing logic

Copilot MUST:
- keep policy separate
- keep logs consistent
- preserve flow integrity
- ensure full traceability
