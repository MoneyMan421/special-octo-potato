import json
from typing import Any, Callable, Dict, Optional


class AuditLogger:
    def __init__(self, sink: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        self._sink = sink

    def log(self, event: str, run_id: str, **fields: Any) -> Dict[str, Any]:
        if not run_id:
            raise ValueError("run_id is required")
        record = {"event": event, "run_id": run_id, **fields}
        if self._sink is not None:
            self._sink(record)
        else:
            print(json.dumps(record, sort_keys=True))
        return record
