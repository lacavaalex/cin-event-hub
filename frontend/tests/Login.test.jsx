import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderApp } from './utils';

const ESPERA = { timeout: 2000 }; // o mock do login simula ~400ms de rede

async function entrar(user, email, senha) {
  await user.type(screen.getByLabelText('E-mail institucional'), email);
  await user.type(screen.getByLabelText('Senha'), senha);
  await user.click(screen.getByRole('button', { name: 'Entrar' }));
}

describe('US 1.1 - Login', () => {
  it('Cenário: campo obrigatório vazio mostra validação no email', async () => {
    const user = userEvent.setup();
    renderApp('/login');

    await user.click(screen.getByRole('button', { name: 'Entrar' }));

    expect(screen.getByText('Informe o e-mail institucional')).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });

  it('Cenário: credenciais inválidas mostram erro e mantêm em /login', async () => {
    const user = userEvent.setup();
    renderApp('/login');

    await entrar(user, 'teste@cin.ufpe.br', 'abc');

    expect(await screen.findByText('Credenciais inválidas', {}, ESPERA)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('Cenário: login bem-sucedido vai para o painel e guarda o token', async () => {
    const user = userEvent.setup();
    renderApp('/login');

    await entrar(user, 'admin@cin.ufpe.br', '123456');

    expect(await screen.findByText('Painel administrativo', {}, ESPERA)).toBeInTheDocument();
    expect(await screen.findByText('Nenhum evento cadastrado.')).toBeInTheDocument();
    expect(window.location.pathname).toBe('/admin');
    expect(localStorage.getItem('token')).toMatch(/^mock\./);
  });

  it('Rota protegida: /admin sem token redireciona para /login', async () => {
    renderApp('/admin');

    expect(await screen.findByRole('button', { name: 'Entrar' })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });
});