"""Avaliação offline da extração por IA sobre o corpus rotulado (US 4.2).

É a ferramenta que operacionaliza a mitigação do risco R2 e a nota de verificação
do backlog: mede **precisão/recall/F1 por campo** do Gemini sobre um corpus
anotado, antes de afirmar a meta de "acerto > 90%".

Uso (com a chave do Gemini configurada em GEMINI_API_KEY):

    cd backend
    python scripts/avaliar_ia.py
    python scripts/avaliar_ia.py --corpus tests/fixtures/corpus_eventos.json --min-f1 0.9

Sem chave, o script encerra explicando que é preciso configurá-la. A extração
estruturada (US 4.1) pode ser avaliada como baseline com ``--baseline``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.extracao_email.parser import parse_email  # noqa: E402
from app.services.ia_gemini.gemini_client import GeminiClient  # noqa: E402
from app.services.ia_gemini.metrics import DEFAULT_FIELDS, evaluate_corpus  # noqa: E402


def _load_corpus(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_extractor(use_baseline: bool):
    if use_baseline:
        return parse_email

    client = GeminiClient()
    if not client.is_configured():
        raise SystemExit(
            "GEMINI_API_KEY não configurada. Defina a variável de ambiente "
            "(ou use --baseline para avaliar o parser estruturado da US 4.1)."
        )
    return client.extract_event


def main() -> int:
    parser = argparse.ArgumentParser(description="Avalia extração de eventos (F1).")
    default_corpus = BACKEND_DIR / "tests" / "fixtures" / "corpus_eventos.json"
    parser.add_argument("--corpus", type=Path, default=default_corpus)
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Avalia o parser estruturado (US 4.1) em vez do Gemini.",
    )
    parser.add_argument("--min-f1", type=float, default=0.9)
    args = parser.parse_args()

    corpus = _load_corpus(args.corpus)
    extractor = _build_extractor(args.baseline)

    result = evaluate_corpus(corpus, extractor, fields=DEFAULT_FIELDS)
    rotulo = "parser estruturado (US 4.1)" if args.baseline else "Gemini (US 4.2)"

    print(f"Avaliação: {rotulo} | corpus={args.corpus.name} | itens={len(corpus)}\n")
    print(f"{'campo':<12}{'precisão':>10}{'recall':>10}{'F1':>10}{'suporte':>10}")
    for field, m in result["per_field"].items():
        print(f"{field:<12}{m.precision:>10.3f}{m.recall:>10.3f}{m.f1:>10.3f}{m.support:>10}")
    macro = result["macro"]
    print(
        f"\nMACRO        {macro.precision:>10.3f}{macro.recall:>10.3f}"
        f"{macro.f1:>10.3f}{macro.support:>10}"
    )

    if macro.f1 < args.min_f1:
        print(f"\nFALHA: F1 macro {macro.f1:.3f} < meta {args.min_f1:.3f}")
        return 1
    print(f"\nOK: F1 macro {macro.f1:.3f} >= meta {args.min_f1:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
