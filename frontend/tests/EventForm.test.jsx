import { describe, it, expect, beforeEach } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderApp } from './utils';

const AVISO_DATA = 'A data do evento não pode ser anterior à data atual';
const botaoCriar = () => screen.getByRole('button', { name: 'Criar Evento' });

// data (AAAA-MM-DD) daqui a N dias, no fuso local
function dia(offset) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return d.toLocaleDateString('sv-SE');
}

async function preencher(user, { titulo = 'Palestra de IA', data = dia(1) } = {}) {
  if (titulo) await user.type(screen.getByLabelText('Título'), titulo);
  await user.type(screen.getByLabelText('Descrição'), 'Conversa sobre IA generativa');
  fireEvent.change(screen.getByLabelText('Data'), { target: { value: data } });
  await user.type(screen.getByLabelText('Hora (24h)'), '1430');
  await user.type(screen.getByLabelText('Local'), 'Auditório do CIn');
  await user.selectOptions(screen.getByLabelText('Tipo'), 'Workshop');
  await user.type(screen.getByLabelText('Link de inscrição'), 'https://exemplo.com');
}

describe('US 2.1 - Criar evento', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'mock.teste.sig'); // simula admin logado
  });

  it('Cenário: criar evento com sucesso', async () => {
    const user = userEvent.setup();
    renderApp('/admin/eventos/novo');

    await preencher(user);
    await user.click(botaoCriar());

    expect(await screen.findByText('Evento criado com sucesso!')).toBeInTheDocument();
    const salvos = JSON.parse(localStorage.getItem('mock_events'));
    expect(salvos).toHaveLength(1);
    expect(salvos[0]).toMatchObject({ titulo: 'Palestra de IA', hora: '14:30', tipo: 'Workshop' });
    expect(screen.getByLabelText('Título')).toHaveValue('');

    // o evento aparece na listagem provisória do painel
    await user.click(screen.getByRole('link', { name: /voltar ao painel/i }));
    expect(await screen.findByText('Palestra de IA')).toBeInTheDocument();
    expect(screen.getByText('Eventos cadastrados (1)')).toBeInTheDocument();
  });

  it('Cenário: campo obrigatório vazio não cria o evento', async () => {
    const user = userEvent.setup();
    renderApp('/admin/eventos/novo');

    await preencher(user, { titulo: '' });
    await user.click(botaoCriar());

    expect(screen.getByText('Informe o título')).toBeInTheDocument();
    expect(localStorage.getItem('mock_events')).toBeNull();
  });

  it('Cenário: data no passado mostra aviso e não cria o evento', async () => {
    const user = userEvent.setup();
    renderApp('/admin/eventos/novo');

    await preencher(user, { data: dia(-1) });
    expect(screen.getByText(AVISO_DATA)).toBeInTheDocument(); // aparece ao escolher a data

    await user.click(botaoCriar());
    expect(screen.getByText(AVISO_DATA)).toBeInTheDocument();
    expect(localStorage.getItem('mock_events')).toBeNull();
  });

  it('Hora em 24h: aplica a máscara HH:MM e rejeita hora inválida', async () => {
    const user = userEvent.setup();
    renderApp('/admin/eventos/novo');
    const hora = screen.getByLabelText('Hora (24h)');

    await user.type(hora, '1430');
    expect(hora).toHaveValue('14:30');

    await user.clear(hora);
    await user.type(hora, '2560');
    await user.click(botaoCriar());
    expect(screen.getByText('Use o formato 24h (ex.: 14:30)')).toBeInTheDocument();
  });
});