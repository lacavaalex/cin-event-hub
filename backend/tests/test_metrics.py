"""Testes da métrica de extração (US 4.2 / risco R2).

Cobrem o cálculo de precisão/recall/F1 e a avaliação sobre o corpus rotulado
(``fixtures/corpus_eventos.json``), usando o parser estruturado como *baseline*
offline — o mesmo ``evaluate_corpus`` é usado pelo script ``scripts/avaliar_ia.py``
para medir o Gemini com uma chave real.
"""

import datetime as dt
import json
from pathlib import Path

from app.services.extracao_email.parser import ParsedEvent, parse_email
from app.services.ia_gemini.metrics import Metrics, evaluate_corpus

CORPUS_PATH = Path(__file__).parent / "fixtures" / "corpus_eventos.json"


def _load_corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_from_counts_calcula_f1():
    m = Metrics.from_counts(tp=8, fp=2, fn=2)
    assert m.precision == 0.8
    assert m.recall == 0.8
    assert m.f1 == 0.8
    assert m.support == 10


def test_from_counts_sem_predicoes():
    m = Metrics.from_counts(tp=0, fp=0, fn=3)
    assert m.precision == 0.0
    assert m.recall == 0.0
    assert m.f1 == 0.0


def test_evaluate_corpus_extrator_perfeito():
    corpus = [
        {"subject": "A", "body": "b", "expected": {"title": "A", "date": "2026-01-01"}},
    ]

    def perfeito(subject, body):
        return {"title": "A", "date": dt.date(2026, 1, 1)}

    result = evaluate_corpus(corpus, perfeito, fields=("title", "date"))
    assert result["macro"].f1 == 1.0
    assert result["per_field"]["date"].recall == 1.0


def test_evaluate_corpus_conta_erro_e_omissao():
    corpus = [
        {"subject": "A", "body": "b", "expected": {"title": "Certa", "location": "X"}},
    ]

    def errado(subject, body):
        # title errado (FP+FN) e location ausente (FN)
        return {"title": "Errada"}

    result = evaluate_corpus(corpus, errado, fields=("title", "location"))
    assert result["per_field"]["title"].f1 == 0.0
    assert result["per_field"]["location"].f1 == 0.0
    # macro: 0 TP, 1 FP, 2 FN
    assert result["macro"].precision == 0.0
    assert result["macro"].recall == 0.0


def test_baseline_parser_estruturado_no_corpus():
    """O parser da US 4.1 serve de linha de base para a meta de 90% (US 4.2)."""
    result = evaluate_corpus(_load_corpus(), parse_email)

    assert result["macro"].f1 >= 0.9, result["per_field"]
    for field, metrics in result["per_field"].items():
        assert metrics.f1 >= 0.8, (field, metrics)


def test_evaluate_corpus_aceita_dataclass():
    corpus = [
        {
            "subject": "Workshop",
            "body": "",
            "expected": {"title": "Workshop", "date": "2026-02-02"},
        }
    ]

    def via_dataclass(subject, body):
        return ParsedEvent(
            title="Workshop",
            date=dt.date(2026, 2, 2),
            time=dt.time(10, 0),
            location="Sala 1",
            description="d",
        )

    result = evaluate_corpus(corpus, via_dataclass, fields=("title", "date"))
    assert result["macro"].f1 == 1.0
