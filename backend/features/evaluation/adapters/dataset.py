"""Dataset adapter: validate before load, expose unchanged base bytes.

Spec ``Validate Before Execution``: the CI dataset validator runs first and any
diagnostic means the harness MUST NOT reach ``load_corpus``. Reuses the
dataset authority without spawning a subprocess. ``base_scenario_payloads``
returns the raw, unchanged bytes of every manifest scenario file ordered by
stable ascending scenario id; the runner (Unit 2) assembles the 34 cases from
these bytes plus the injected failure pair.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from backend.features.corpus.adapters.manifest_loader import load_corpus
from backend.features.corpus.application import Corpus
from scripts.ci.validate_evaluation_dataset import validate as validate_dataset

MANIFEST_FILENAME: Final[str] = "manifest.json"


class DatasetValidationError(Exception):
    """Fail-closed error when the dataset validator returns findings.

    Lists only the finding count; never includes content (safe-field contract).
    """

    __slots__ = ("finding_count",)

    def __init__(self, finding_count: int) -> None:
        self.finding_count = finding_count
        super().__init__(f"dataset-validation-failed: {finding_count} findings")


def load_validated_corpus(root: Path, *, profile: str) -> Corpus:
    """Validate the dataset root, then load the development-only corpus.

    Any diagnostic raises :class:`DatasetValidationError` and ``load_corpus`` is
    never called, so the kernel and provider never execute on an invalid dataset.
    """
    findings = validate_dataset(root)
    if findings:
        raise DatasetValidationError(len(findings))
    return load_corpus(root / MANIFEST_FILENAME, profile=profile)


def base_scenario_payloads(root: Path) -> dict[str, bytes]:
    """Return the unchanged bytes of every manifest scenario, keyed by id.

    Reads only manifest-listed scenario files in canonical byte order (sorted
    by scenario id); bytes are returned exactly as stored on disk.
    """
    manifest = json.loads((root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    entries = sorted(
        (a["id"], a["path"]) for a in manifest.get("artifacts", []) if a.get("kind") == "scenario"
    )
    return {scenario_id: (root / path).read_bytes() for scenario_id, path in entries}
