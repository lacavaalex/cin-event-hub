import { render } from '@testing-library/react';
import App from '../src/App';

// renderiza o app inteiro (com rotas) já na URL desejada
export function renderApp(path = '/login') {
  window.history.pushState({}, '', path);
  return render(<App />);
}