"""Safe report adapter: allowlisted serialization and atomic baseline retention.

Serializes only safe fields: IDs, enums, versions, timestamps, booleans, counts,
rates, profile, and duration. Never emits question/answer/citation content,
claim text, or provider payloads.

Baseline retention is atomic: ``current/`` holds the latest reviewed baseline;
``previous/`` is created only when a later replacement exists. Incomplete
promotions (empty payload) are rejected with no baseline written.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from backend.features.evaluation.application import RunSummary


def _metric_dict(signal: object) -> dict[str, int]:
    return {"numerator": signal.numerator, "denominator": signal.denominator}  # type: ignore[attr-defined]


def serialize_summary(summary: RunSummary) -> str:
    """JSON summary with allowlisted fields only."""
    m = summary.metrics
    data = {
        "run_id": summary.identity.run_id,
        "contract_version": "1",
        "profile": "development",
        "provider_mode": "fake",
        "total_cases": len(summary.results),
        "timestamp": None,
        "duration_seconds": None,
        "metrics": {
            "outcome_classification": _metric_dict(m.outcome_classification),
            "citation_exact_match": _metric_dict(m.citation_exact_match),
            "language_routing": _metric_dict(m.language_routing),
            "sensitive_block": _metric_dict(m.sensitive_block),
            "contradiction_detection": _metric_dict(m.contradiction_detection),
        },
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def serialize_records(summary: RunSummary) -> str:
    """JSONL scenario rows, one per case, allowlisted fields only."""
    lines: list[str] = []
    for result in summary.results:
        record = {
            "case_id": result.case_id,
            "language": result.language,
            "observed_outcome": result.observed_outcome,
            "reason_code": result.reason_code,
            "citation_ids": list(result.citation_ids),
            "citations_match": result.citations_match,
        }
        lines.append(json.dumps(record, sort_keys=True, separators=(",", ":")))
    return "\n".join(lines)


def serialize_human(summary: RunSummary) -> str:
    """Concise human-readable output; safe fields only, no content."""
    m = summary.metrics
    oc = m.outcome_classification
    ce = m.citation_exact_match
    lr = m.language_routing
    sb = m.sensitive_block
    cd = m.contradiction_detection
    lines = [
        "OpsKnowledge quality evaluation",
        f"run_id: {summary.identity.run_id}",
        "profile: development",
        f"total_cases: {len(summary.results)}",
        f"outcome_classification: {oc.numerator}/{oc.denominator}",
        f"citation_exact_match: {ce.numerator}/{ce.denominator}",
        f"language_routing: {lr.numerator}/{lr.denominator}",
        f"sensitive_block: {sb.numerator}/{sb.denominator}",
        f"contradiction_detection: {cd.numerator}/{cd.denominator}",
    ]
    return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class ReportAdapter:
    """Atomic baseline store: at most current + previous."""

    base_dir: Path

    def promote(self, run_id: str, payload: bytes) -> None:
        if not payload:
            raise ValueError("incomplete-promotion: empty payload")
        current = self.base_dir / "current"
        previous = self.base_dir / "previous"
        staged = self.base_dir / f".staging-{run_id}"
        staged.mkdir(parents=True, exist_ok=True)
        (staged / "summary.json").write_bytes(payload)
        if current.exists():
            if previous.exists():
                shutil.rmtree(previous)
            os.replace(current, previous)
        os.replace(staged, current)
