# Paginação da listagem de eventos (IESI-71 e IESI-70)

## Contrato do `GET /events`

| Parâmetro | Tipo | Padrão | Regra |
|-----------|------|--------|-------|
| `page` | inteiro | `1` | começa em 1; `0`, negativo ou texto → **422** |
| `page_size` | inteiro | `20` | de 1 a 100; fora disso → **422** |

Resposta `200`:

```json
{
  "items": [ { "id": 1, "title": "...", "date": "2026-10-20", "time": "09:00:00", "...": "..." } ],
  "page": 1,
  "total_pages": 3
}
```

- `items`: eventos **ativos** da página, em ordem cronológica (data, hora, id).
- `page`: a página pedida. Há próxima página enquanto `page < total_pages`.
- `total_pages`: `ceil(total de eventos ativos / page_size)`; `0` quando não há eventos.
- Página além do total: `200` com `items: []` (o cliente sabe onde parar por `total_pages`).

Sem parâmetros, a rota devolve os 20 primeiros eventos.

## Como a consulta funciona (IESI-71)

`event_repository.get_all(db, limit=20, offset=0)` gera, em PostgreSQL:

```sql
SELECT ... FROM events
WHERE status = 'active'
ORDER BY date, time, id
LIMIT :limit OFFSET :offset
```

e `offset = (page - 1) * page_size`, calculado no serviço (`event_service.list_events`).
O total de páginas usa `event_repository.count_active` (`SELECT count(id) ... WHERE status = 'active'`).

## Decisões e trade-offs

| Decisão | Motivo | Alternativa descartada |
|---------|--------|------------------------|
| `ORDER BY date, time, id` | LIMIT/OFFSET sem ordem total pode repetir ou perder eventos entre páginas; o `id` desempata. A hora entra porque o frontend ordena por data **e hora** (`sortByDate`) — ordenar só por data deixaria as páginas inconsistentes com a tela. | Só `date` (como era): eventos do mesmo dia trocam de página. |
| Corpo `{items, page, total_pages}` | Contrato explícito e extensível. | Metadados em headers (`X-Total-Pages`): mantém o array, mas exige `expose_headers` no CORS e é incomum de consumir. |
| `page`/`page_size` (a página começa em 1) | Nomes mais comuns; o front calcula "próxima página" sem aritmética de offset. | `limit`/`offset` direto na URL. |
| Teto de `page_size = 100` | Sem teto, `page_size=1000000` anula o LIMIT. **É a única regra além do texto da task**; se o time não quiser, basta tirar o `le=` da rota. | Sem teto. |
| Página inexistente → lista vazia | Mais simples para o cliente do que tratar 404. | 404 / 422. |
| `total_pages = 0` sem eventos | Honesto: não há página alguma. | Forçar 1. |

## Impacto no frontend

O formato da resposta mudou de lista para objeto. Para a **Home não quebrar**, o
`getEvents()` em `frontend/src/services/eventService.js` ganhou uma linha que aceita os
dois formatos (`Array.isArray(data) ? data : data.items`). Hoje a Home mostra só a
primeira página (20 eventos); o botão/controle de próxima página é a **IESI-72** (front).

## Testes

- `backend/tests/repositories/test_event_repository.py` — LIMIT/OFFSET em PostgreSQL (IESI-71).
- `backend/tests/services/test_event_service.py` — offset e total de páginas (IESI-70).
- `backend/tests/api/test_list_events.py` — a rota de ponta a ponta (IESI-70).

```bash
python -m pytest backend
```
