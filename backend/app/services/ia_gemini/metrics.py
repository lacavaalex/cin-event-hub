from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterable
from dataclasses import dataclass

DEFAULT_FIELDS = ("title", "date", "time", "location")


@dataclass(frozen=True)
class Metrics:
    """Precisão, recall e F1 de um único campo (ou agregado)."""

    precision: float
    recall: float
    f1: float
    support: int  # total de valores esperados (TP + FN + FP na contagem usada)

    @classmethod
    def from_counts(cls, tp: int, fp: int, fn: int) -> Metrics:
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        return cls(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            support=tp + fn,
        )


def _normalize(field: str, value: object) -> str:
    """Normaliza o valor para comparação estável (texto, datas e horas)."""
    if value is None:
        return ""
    if isinstance(value, dt.date | dt.datetime):
        return value.isoformat()
    if isinstance(value, dt.time):
        return value.strftime("%H:%M")
    text = str(value).strip().lower()
    if field == "date":
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return dt.datetime.strptime(text, fmt).date().isoformat()
            except ValueError:
                continue
    if field == "time":
        text = text.replace("h", ":")
        if text.endswith(":"):
            text += "00"
    return text


def evaluate_corpus(
    corpus: Iterable[dict],
    extractor: Callable[[str, str], dict | object],
    fields: tuple[str, ...] = DEFAULT_FIELDS,
) -> dict:
    """Avalia um extrator sobre um corpus rotulado.

    ``corpus``: iterável de ``{"subject": str, "body": str, "expected": {...}}``.
    ``extractor``: callable ``(subject, body) -> mapping|objeto`` com os campos.
    Retorna ``{"per_field": {campo: Metrics}, "macro": Metrics}``.
    """
    counts = {field: {"tp": 0, "fp": 0, "fn": 0} for field in fields}

    for item in corpus:
        expected = item.get("expected", {})
        try:
            predicted = extractor(item.get("subject", ""), item.get("body", ""))
        except Exception:
            predicted = {}
        predicted = _as_mapping(predicted)

        for field in fields:
            gold = _normalize(field, expected.get(field))
            got = _normalize(field, predicted.get(field)) if predicted else ""
            if gold and got == gold:
                counts[field]["tp"] += 1
            elif not got and gold:
                counts[field]["fn"] += 1
            elif got and got != gold:
                counts[field]["fp"] += 1
                if gold:
                    counts[field]["fn"] += 1

    per_field = {
        field: Metrics.from_counts(**counts[field]) for field in fields
    }
    macro_tp = sum(c["tp"] for c in counts.values())
    macro_fp = sum(c["fp"] for c in counts.values())
    macro_fn = sum(c["fn"] for c in counts.values())
    return {"per_field": per_field, "macro": Metrics.from_counts(macro_tp, macro_fp, macro_fn)}


def _as_mapping(obj: object) -> dict:
    """Aceita dict ou dataclass (ex.: ``ParsedEvent``)."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return vars(obj)
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(obj)
    return {}
