"""Evidence validation helpers for ASTA sidecar outputs (PE5)."""

from __future__ import annotations


def validate_evidence_spans(record: dict, spans: list[str]) -> list[dict]:
    """
    Validate evidence spans by checking case-insensitive substring presence
    in record title + abstract.
    """
    title = str(record.get("title") or "")
    abstract = str(record.get("abstract") or "")
    text = f"{title} {abstract}".lower()

    validated: list[dict] = []
    for span in spans:
        s = str(span or "")
        validated.append({"text": s, "valid": bool(s and s.lower() in text)})
    return validated
