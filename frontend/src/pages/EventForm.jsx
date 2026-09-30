import { useState } from 'react';
import { Link } from 'react-router-dom';
import { createEvent, EVENT_TYPES } from '../services/eventService';
import '../styles/event-form.css';

const EMPTY = { titulo: '', descricao: '', data: '', hora: '', local: '', tipo: '', linkInscricao: '' };

// data de hoje no fuso local, formato AAAA-MM-DD
const today = () => new Date().toLocaleDateString('sv-SE');

// máscara HH:MM (24h): só dígitos, com ":" inserido automaticamente
function maskHora(value) {
  const d = value.replace(/\D/g, '').slice(0, 4);
  return d.length > 2 ? `${d.slice(0, 2)}:${d.slice(2)}` : d;
}

function validate(f) {
  const e = {};
  if (!f.titulo.trim()) e.titulo = 'Informe o título';
  if (!f.descricao.trim()) e.descricao = 'Informe a descrição';

  if (!f.data) e.data = 'Informe a data';
  else if (f.data < today()) e.data = 'A data do evento não pode ser anterior à data atual';

  if (!f.hora) e.hora = 'Informe a hora';
  else if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(f.hora)) e.hora = 'Use o formato 24h (ex.: 14:30)';

  if (!f.local.trim()) e.local = 'Informe o local';
  if (!f.tipo) e.tipo = 'Selecione o tipo';

  if (!f.linkInscricao.trim()) e.linkInscricao = 'Informe o link de inscrição';
  else if (!/^https?:\/\/\S+$/i.test(f.linkInscricao.trim()))
    e.linkInscricao = 'Informe um link válido (ex.: https://...)';

  return e;
}

export default function EventForm() {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);

  const field = (name) => ({
    id: name,
    name,
    value: form[name],
    onChange: handleChange,
    className: errors[name] ? 'invalid' : '',
  });
  const err = (name) => errors[name] && <span className="event-error">{errors[name]}</span>;

  function handleChange(e) {
    const { name } = e.target;
    const value = name === 'hora' ? maskHora(e.target.value) : e.target.value;

    const next = { ...form, [name]: value };
    setForm(next);
    setSuccess('');

    // a data é validada assim que é escolhida; os demais campos limpam o erro ao serem corrigidos
    if (name === 'data' || errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: validate(next)[name] }));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSuccess('');
    setFormError('');

    const found = validate(form);
    setErrors(found);
    if (Object.keys(found).length) return;

    setLoading(true);
    try {
      const data = Object.fromEntries(Object.entries(form).map(([k, v]) => [k, v.trim()]));
      await createEvent(data);
      setForm(EMPTY);
      setSuccess('Evento criado com sucesso!');
    } catch (error) {
      setFormError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="event-page">
      <form className="event-card" onSubmit={handleSubmit} noValidate>
        <Link to="/admin" className="event-back">← Voltar ao painel</Link>
        <h1>Criar novo evento</h1>

        {success && <div className="event-alert success" role="status">{success}</div>}
        {formError && <div className="event-alert error" role="alert">{formError}</div>}

        <div className="event-field">
          <label htmlFor="titulo">Título</label>
          <input {...field('titulo')} />
          {err('titulo')}
        </div>

        <div className="event-field">
          <label htmlFor="descricao">Descrição</label>
          <textarea {...field('descricao')} />
          {err('descricao')}
        </div>

        <div className="event-row">
          <div className="event-field">
            <label htmlFor="data">Data</label>
            <input type="date" {...field('data')} />
            {err('data')}
          </div>
          <div className="event-field">
            <label htmlFor="hora">Hora (24h)</label>
            <input
              type="text"
              inputMode="numeric"
              placeholder="HH:MM"
              maxLength={5}
              {...field('hora')}
            />
            {err('hora')}
          </div>
        </div>

        <div className="event-field">
          <label htmlFor="local">Local</label>
          <input {...field('local')} />
          {err('local')}
        </div>

        <div className="event-field">
          <label htmlFor="tipo">Tipo</label>
          <select {...field('tipo')}>
            <option value="">Selecione...</option>
            {EVENT_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          {err('tipo')}
        </div>

        <div className="event-field">
          <label htmlFor="linkInscricao">Link de inscrição</label>
          <input type="url" placeholder="https://..." {...field('linkInscricao')} />
          {err('linkInscricao')}
        </div>

        <button className="event-submit" type="submit" disabled={loading}>
          {loading ? 'Criando...' : 'Criar Evento'}
        </button>
      </form>
    </main>
  );
}