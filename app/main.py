from typing import Any, Optional
from uuid import uuid4

from observability.audit import AuditLogger
from policy.gate import classify_input


def core_process(payload: Any) -> Any:
    return payload


def handle_request(payload: Any, logger: Optional[AuditLogger] = None) -> Any:
    run_id = str(uuid4())
    active_logger = logger or AuditLogger()

    active_logger.log("request_started", run_id, payload=payload)
    warnings = classify_input(payload)
    if warnings:
        active_logger.log("policy_warning", run_id, warnings=warnings)

    result = core_process(payload)
    active_logger.log("request_completed", run_id, result=result)
    return result
