"""Reviewed ES/EN question mapping for the evaluation harness.

Harness-owned question surface, NOT dataset metadata and NOT answer ground
truth: each row maps a scenario id to a deterministic, non-empty question in
the scenario's declared language. Unreviewed rows fail closed at
:func:`validate_mapping`. Rows are ordered by stable ascending scenario id.
"""

from __future__ import annotations

import hashlib
from typing import Final

from backend.features.evaluation.domain import QuestionMapping

# Reviewed question text per scenario (input only; never answer ground truth).
_ES_QUESTIONS: Final[dict[str, str]] = {
    "scenario.eval-01.es": "Cual es el procedimiento aprobado en el runbook de operaciones?",
    "scenario.eval-02.es": "Que politica operacional aplica a la entrada referenciada?",
    "scenario.eval-03.es": "Cual es la revision vigente del runbook de operaciones?",
    "scenario.eval-04.es": "Que dice el fragmento OCR de calidad sobre la operacion?",
    "scenario.eval-05.es": "Cual es el primer paso aprobado del runbook de operaciones?",
    "scenario.eval-06.es": "Que politica operacional rige la entrada referenciada?",
    "scenario.eval-07.es": "Cual es el contenido OCR de calidad sobre la operacion?",
    "scenario.eval-08.es": "Cual es la segunda revision aprobada del runbook?",
    "scenario.eval-09.es": "La informacion del fragmento es suficiente para responder?",
    "scenario.eval-10.es": "La entrada referenciada esta completa o es ambigua?",
    "scenario.eval-11.es": "Existen revisiones contradictorias del mismo runbook?",
    "scenario.eval-12.es": "Hay contradiccion entre revisiones aprobadas del runbook?",
    "scenario.eval-13.es": "Cual es la condicion fuera de alcance del escenario?",
    "scenario.eval-14.es": "El proveedor esta disponible para esta consulta operacional?",
    "scenario.eval-15.es": "La solicitud ignora el contexto de citas aprobadas?",
    "scenario.eval-16.es": "La consulta contiene un identificador sensible bloqueado?",
}
_EN_QUESTIONS: Final[dict[str, str]] = {
    "scenario.eval-01.en": "What is the approved procedure in the operations runbook?",
    "scenario.eval-02.en": "Which operational policy applies to the referenced entry?",
    "scenario.eval-03.en": "What is the current revision of the operations runbook?",
    "scenario.eval-04.en": "What does the OCR quality fragment say about the operation?",
    "scenario.eval-05.en": "What is the first approved step of the operations runbook?",
    "scenario.eval-06.en": "Which operational policy governs the referenced entry?",
    "scenario.eval-07.en": "What is the OCR quality content about the operation?",
    "scenario.eval-08.en": "What is the second approved revision of the runbook?",
    "scenario.eval-09.en": "Is the fragment information sufficient to answer?",
    "scenario.eval-10.en": "Is the referenced entry complete or ambiguous?",
    "scenario.eval-11.en": "Are there contradictory revisions of the same runbook?",
    "scenario.eval-12.en": "Is there a contradiction between approved runbook revisions?",
    "scenario.eval-13.en": "What is the out-of-scope condition for the scenario?",
    "scenario.eval-14.en": "Is the provider available for this operational query?",
    "scenario.eval-15.en": "Does the request ignore the approved citation context?",
    "scenario.eval-16.en": "Does the query contain a blocked sensitive identifier?",
}


def _build_rows() -> tuple[QuestionMapping, ...]:
    rows: list[QuestionMapping] = []
    for scenario_id in sorted((*_ES_QUESTIONS, *_EN_QUESTIONS)):
        if scenario_id in _ES_QUESTIONS:
            rows.append(QuestionMapping(scenario_id, "es", _ES_QUESTIONS[scenario_id], True))
        else:
            rows.append(QuestionMapping(scenario_id, "en", _EN_QUESTIONS[scenario_id], True))
    return tuple(rows)


REVIEWED_MAPPING: Final[tuple[QuestionMapping, ...]] = _build_rows()


class MappingError(Exception):
    """Fail-closed mapping validation error with a safe reason code."""

    __slots__ = ("reason_code",)

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def validate_mapping(
    rows: tuple[QuestionMapping, ...],
    expected_scenario_ids: list[str],
    scenario_languages: dict[str, str],
) -> tuple[QuestionMapping, ...]:
    """Validate the mapping against the dataset scenario contract.

    Fails closed on missing, duplicate, unknown, unreviewed, empty-question,
    or language-mismatched rows. Returns the validated, ordered rows.
    """
    expected = set(expected_scenario_ids)
    seen: set[str] = set()
    for row in rows:
        if row.scenario_id not in expected:
            raise MappingError("mapping-unknown-scenario-id")
        if row.scenario_id in seen:
            raise MappingError("mapping-duplicate-scenario-id")
        seen.add(row.scenario_id)
        if not row.reviewed:
            raise MappingError("mapping-row-not-reviewed")
        if row.language != scenario_languages[row.scenario_id]:
            raise MappingError("mapping-language-mismatch")
        if not row.question:
            raise MappingError("mapping-empty-question")
    if seen != expected:
        raise MappingError("mapping-missing-scenario-id")
    return tuple(sorted(rows, key=lambda r: r.scenario_id))


def mapping_digest(rows: tuple[QuestionMapping, ...]) -> str:
    """Stable sha256 hex digest over the reviewed mapping bytes (part of run identity)."""
    material = "\n".join(
        f"{row.scenario_id}|{row.language}|{row.reviewed}|{row.question}" for row in rows
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
