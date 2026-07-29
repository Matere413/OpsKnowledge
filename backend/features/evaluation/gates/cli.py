"""Technical grounding safety gate CLI entry point: opt-in release contract.

Invoked only through ``make eval-quality-gate``. Uses the frozen clock for
deterministic output, runs the unchanged 34-case evaluation via the harness,
evaluates the gate (critical contracts + floor policy), serializes the safe
gate report, and promotes it atomically under ``evaluation-runs/gate/``.

No subprocess, no shell evaluation, no network, no persistence beyond
``evaluation-runs/gate/``. ``block`` and ``escalate`` exit non-zero; ``escalate``
uses the normal gate report, not a separate record.
"""

from __future__ import annotations

import sys
from pathlib import Path

from backend.features.evaluation.adapters.clock import FrozenClock
from backend.features.evaluation.application import run_evaluation
from backend.features.evaluation.gates.adapters.report import (
    GateReportAdapter,
    bootstrap_baseline,
    serialize_gate_report,
)
from backend.features.evaluation.gates.application import evaluate_gate

_FROZEN_TIMESTAMP = 1_700_000_000.0
_FROZEN_DURATION = 0.0
_PROJECT_ROOT = Path(__file__).resolve().parents[4]


def run_gate(
    *,
    dataset_root: Path,
    gate_dir: Path,
    harness_current: Path,
    clock: FrozenClock,
) -> int:
    """Run the gate end-to-end and return the process exit code.

    Returns 0 for ``pass`` and non-zero for ``block``/``escalate``. The gate
    report is always promoted (even on non-pass) so reviewers see the safe
    evidence; ``escalate`` uses the normal report, not a separate record.
    """
    summary = run_evaluation(dataset_root, clock=clock)
    baseline = bootstrap_baseline(gate_dir=gate_dir, harness_current=harness_current)
    decision = evaluate_gate(summary=summary, baseline=baseline)

    payload = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=baseline,
        profile="development",
        provider_mode="fake",
        timestamp=clock.now(),
        duration_seconds=clock.elapsed_since_start(),
    )
    adapter = GateReportAdapter(base_dir=gate_dir)
    adapter.promote(run_id=summary.identity.run_id, payload=payload)

    # Safe stdout: status and reason codes only, no content.
    sys.stdout.write(f"gate: {decision.status}\nreasons: {','.join(decision.reason_codes)}\n")

    if decision.status == "pass":
        return 0
    return 1


def main() -> int:
    dataset_root = Path(sys.argv[1]) if len(sys.argv) > 1 else _PROJECT_ROOT / "evaluation-dataset"
    if not dataset_root.is_absolute():
        dataset_root = _PROJECT_ROOT / dataset_root
    gate_dir = _PROJECT_ROOT / "evaluation-runs" / "gate"
    harness_current = _PROJECT_ROOT / "evaluation-runs" / "current"
    clock = FrozenClock(timestamp=_FROZEN_TIMESTAMP, duration_seconds=_FROZEN_DURATION)
    return run_gate(
        dataset_root=dataset_root,
        gate_dir=gate_dir,
        harness_current=harness_current,
        clock=clock,
    )


if __name__ == "__main__":
    raise SystemExit(main())
