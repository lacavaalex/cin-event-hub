import LogoutButton from '../components/LogoutButton';

export default function Dashboard() {
  return (
    <main style={{ padding: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: 'var(--red)' }}>Painel administrativo</h1>
        <LogoutButton />
      </header>
      <p>Login realizado com sucesso.</p>
    </main>
  );
}