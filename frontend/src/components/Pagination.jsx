function getPageItems(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  const items = [1];
  const from = Math.max(2, current - 1);
  const to = Math.min(total - 1, current + 1);
  if (from > 2) items.push('gap-start');
  for (let p = from; p <= to; p++) items.push(p);
  if (to < total - 1) items.push('gap-end');
  items.push(total);
  return items;
}

export default function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;

  return (
    <nav className="pagination" aria-label="Paginação da lista de eventos">
      <button
        type="button"
        className="pagination-btn"
        onClick={() => onChange(page - 1)}
        disabled={page === 1}
      >
        ← Anterior
      </button>

      <ul className="pagination-pages">
        {getPageItems(page, totalPages).map((item) =>
          typeof item === 'number' ? (
            <li key={item}>
              <button
                type="button"
                className="pagination-btn pagination-num"
                aria-label={`Página ${item}`}
                aria-current={item === page ? 'page' : undefined}
                onClick={() => onChange(item)}
              >
                {item}
              </button>
            </li>
          ) : (
            <li key={item} className="pagination-gap" aria-hidden="true">…</li>
          )
        )}
      </ul>

      <button
        type="button"
        className="pagination-btn"
        onClick={() => onChange(page + 1)}
        disabled={page === totalPages}
      >
        Próxima →
      </button>
    </nav>
  );
}