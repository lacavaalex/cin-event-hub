const API_URL = import.meta.env.VITE_API_URL;
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const LONG_DESC =
  'Uma tarde inteira dedicada a inteligência artificial generativa. Vamos falar sobre como funcionam os modelos de linguagem, o que mudou nos últimos anos e quais são as aplicações práticas em empresas, pesquisa e educação. Haverá demonstrações ao vivo, discussão sobre limites e riscos, e um momento final de perguntas com os palestrantes. Traga seu notebook se quiser acompanhar os exemplos em código.';

const MOCK_EVENTS = [
  { id: 1, title: 'Hackathon CIn 2026', description: 'Maratona de 24h.', date: '2026-11-07', time: '09:00', location: 'Térreo do CIn', type: 'Hackathon', registration_link: 'https://example.com/hackathon' },
  { id: 2, title: 'Palestra de IA Generativa', description: LONG_DESC, date: '2026-10-20', time: '19:00', location: 'Auditório do CIn', type: 'Palestra', registration_link: 'https://example.com/palestra-ia' },
  { id: 3, title: 'Workshop de React', description: 'Do zero ao primeiro app.', date: '2026-10-20', time: '14:00', location: 'Sala E112', type: 'Workshop', registration_link: 'https://example.com/react' },
  { id: 4, title: 'Minicurso de Git e GitHub', description: 'Fluxo de trabalho em equipe.', date: '2026-10-28', time: '10:30', location: 'Laboratório G4', type: 'Minicurso', registration_link: 'https://example.com/git' },
  { id: 5, title: 'Palestra sobre Machine Learning', description: 'Casos reais na indústria.', date: '2026-10-15', time: '16:00', location: 'Auditório do CIn', type: 'Palestra', registration_link: 'https://example.com/ml' },
  { id: 6, title: 'Workshop de UX para Devs', description: 'Pesquisa e prototipação.', date: '2026-12-02', time: '15:00', location: 'Sala A215', type: 'Workshop', registration_link: 'https://example.com/ux' },
];

export function sortByDate(events) {
  return [...events].sort((a, b) =>
    `${a.date}T${a.time}`.localeCompare(`${b.date}T${b.time}`)
  );
}

export async function getEvents() {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 400));
    return MOCK_EVENTS;
  }
  let res;
  try {
    res = await fetch(`${API_URL}/events`);
  } catch {
    throw new Error('Erro de conexão. Tente novamente.');
  }
  if (!res.ok) throw new Error('Não foi possível carregar os eventos.');
  return res.json();
}

export async function getEventById(id) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const event = MOCK_EVENTS.find((e) => String(e.id) === String(id));
    if (!event) throw new Error('NOT_FOUND');
    return event;
  }
  let res;
  try {
    res = await fetch(`${API_URL}/events/${id}`);
  } catch {
    throw new Error('Erro de conexão. Tente novamente.');
  }
  if (res.status === 404) throw new Error('NOT_FOUND');
  if (!res.ok) throw new Error('Não foi possível carregar o evento.');
  return res.json();
}

function normalize(text) {
  return String(text ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // ignora acentos
    .toLowerCase()
    .trim();
}

// Busca o termo (como trecho contínuo) no título OU na descrição
export function filterByKeyword(events, term) {
  const q = normalize(term);
  if (!q) return events;
  return events.filter(
    (e) => normalize(e.title).includes(q) || normalize(e.description).includes(q)
  );
}

// Eventos extras só para testar a paginação (US 3.6): 6 originais + 44 = 50
MOCK_EVENTS.push(
  ...Array.from({ length: 44 }, (_, i) => ({
    id: 100 + i,
    title: `Encontro de estudos ${String(i + 1).padStart(2, '0')}`,
    description: 'Evento gerado para testar a paginação.',
    date: `2027-01-${String(1 + (i % 28)).padStart(2, '0')}`,
    time: `${String(8 + (i % 10)).padStart(2, '0')}:00`,
    location: 'Sala A101',
    type: ['Workshop', 'Minicurso', 'Hackathon'][i % 3],
    registration_link: 'https://example.com/encontro',
  }))
);