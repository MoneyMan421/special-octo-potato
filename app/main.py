from typing import Any, Dict, Optional
from uuid import uuid4

from observability.audit import AuditLogger
from policy.gate import classify_input


def core_process(payload: Any) -> Any:
    return payload


def planner(context: Dict[str, Any]) -> str:
    direction = context.get("direction", "forward")
    iteration = context.get("iteration", 0)
    return f"{direction}:step-{iteration}"


def executor(plan: str, payload: Any) -> Any:
    _ = plan
    return core_process(payload)


def evaluator(context: Dict[str, Any], plan: str, output: Any) -> Dict[str, Any]:
    stagnant = context.get("last_plan") == plan and context.get("last_output") == output
    return {"stagnant": stagnant}


def controller(context: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
    if evaluation["stagnant"]:
        context["direction"] = f"shift-{context.get('iteration', 0) + 1}"
        context["mutation_count"] = context.get("mutation_count", 0) + 1
        return "direction_shift"
    return "advance"


def handle_request(payload: Any, logger: Optional[AuditLogger] = None) -> Any:
    run_id = str(uuid4())
    active_logger = logger or AuditLogger()

    active_logger.log("request_started", run_id, payload=payload)
    warnings = classify_input(payload)
    if warnings:
        active_logger.log("policy_warning", run_id, warnings=warnings)

    context: Dict[str, Any] = {
        "iteration": 0,
        "direction": "forward",
        "last_plan": None,
        "last_output": None,
    }
    result = payload

    for _ in range(3):
        plan = planner(context)
        active_logger.log("planner", run_id, plan=plan, iteration=context["iteration"])

        candidate = executor(plan, payload)
        active_logger.log("executor", run_id, plan=plan, iteration=context["iteration"])

        evaluation = evaluator(context, plan, candidate)
        active_logger.log(
            "evaluator",
            run_id,
            plan=plan,
            iteration=context["iteration"],
            stagnant=evaluation["stagnant"],
        )

        action = controller(context, evaluation)
        active_logger.log(
            "controller",
            run_id,
            action=action,
            iteration=context["iteration"],
            direction=context["direction"],
        )

        context["last_plan"] = plan
        context["last_output"] = candidate
        context["iteration"] += 1
        result = candidate
        if action == "advance":
            break

    active_logger.log("request_completed", run_id, result=result)
    return result
