"""Evaluation CLI entry point: opt-in quality harness runner.

Invoked only through ``make eval-quality``. Uses the frozen clock for
deterministic output, runs the full 34-case evaluation, serializes safe
reports, and promotes the baseline atomically. No subprocess, no shell
evaluation, no network, no persistence beyond ``evaluation-runs/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from backend.features.evaluation.adapters.clock import FrozenClock
from backend.features.evaluation.adapters.report import (
    ReportAdapter,
    serialize_human,
    serialize_records,
    serialize_summary,
)
from backend.features.evaluation.application import run_evaluation

_FROZEN_TIMESTAMP = 1_700_000_000.0
_FROZEN_DURATION = 0.0
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    dataset_root = Path(sys.argv[1]) if len(sys.argv) > 1 else _PROJECT_ROOT / "evaluation-dataset"
    if not dataset_root.is_absolute():
        dataset_root = _PROJECT_ROOT / dataset_root
    eval_runs = _PROJECT_ROOT / "evaluation-runs"
    clock = FrozenClock(timestamp=_FROZEN_TIMESTAMP, duration_seconds=_FROZEN_DURATION)
    summary = run_evaluation(dataset_root, clock=clock)
    payload = serialize_summary(summary).encode("utf-8")
    records = serialize_records(summary)
    human = serialize_human(summary)
    adapter = ReportAdapter(base_dir=eval_runs)
    adapter.promote(
        run_id=summary.identity.run_id,
        payload=payload,
        records=records,
        report=human,
    )
    sys.stdout.write(human)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
