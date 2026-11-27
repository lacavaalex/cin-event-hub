"""Conftest na raiz do backend: garante que `app` seja importável nos testes.

Ao subir este arquivo na raiz, o pytest insere `backend/` no sys.path e os
testes podem usar `from app...` sem configuração adicional.
"""