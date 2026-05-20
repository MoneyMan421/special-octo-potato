from typing import Any, List


SENSITIVE_KEYWORDS = ("password", "token", "secret")


def classify_input(payload: Any) -> List[str]:
    text = str(payload).lower()
    warnings: List[str] = []

    if any(keyword in text for keyword in SENSITIVE_KEYWORDS):
        warnings.append("contains_sensitive_keyword")
    if len(text) > 500:
        warnings.append("large_payload")

    return warnings
