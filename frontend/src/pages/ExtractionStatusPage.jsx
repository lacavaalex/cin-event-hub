
import { useEffect, useState } from 'react';
import { getExtractionStatus, getExtractionAlerts } from '../services/extractionService';
import '../styles/extraction-status.css';

function formatDateTime(dateString) {
  if (!dateString) {
    return 'Nunca executado';
  }

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return 'Data indisponível';
  }

  return date.toLocaleString('pt-BR', {
    timeZone: 'America/Recife',
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export default function ExtractionStatusPage() {
  const [status, setStatus] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setErrorMessage('');

      try {
        const [statusData, alertsData] = await Promise.all([
          getExtractionStatus(),
          getExtractionAlerts()
        ]);

        setStatus(statusData);
        setAlerts(alertsData);
      } catch {
        setErrorMessage('Não foi possível carregar o painel de extração.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <main className='extraction-page'>
        <h1>Status de Extração</h1>
        <p role='status'>Carregando informações...</p>
      </main>
    );
  }

  if (errorMessage) {
    return (
      <main className='extraction-page'>
        <h1>Status de Extração</h1>
        <div className='extraction-banner extraction-banner-error' role='alert'>
          {errorMessage}
        </div>
      </main>
    );
  }

  const hasFailure = status?.last_run_failed === true;
  const hasRun = Boolean(status?.last_run_at);
  const errorCount = status?.counts_by_status?.erro ?? 0;

  const recentProcessed = status?.recent_processed ?? [];

  return (
    <main className='extraction-page'>
      <div className='extraction-header'>
        <div>
          <p className={`extraction-kicker${hasFailure ? ' extraction-kicker-error' : ''}`}>
            {hasFailure
              ? '● FALHA NA ÚLTIMA EXTRAÇÃO.'
              : hasRun
                ? '● ÚLTIMA EXECUÇÃO REGISTRADA.'
                : '● EXTRAÇÃO AINDA NÃO EXECUTADA.'}
          </p>

          <h1>Status de Extração</h1>
        </div>
      </div>

      {hasFailure && (
        <div className='extraction-banner extraction-banner-error' role='alert'>
          <strong>Falha na extração de e-mails</strong>
          <p>
            {status?.last_error ||
              'Foi identificada uma falha no serviço de extração.'}
          </p>
        </div>
      )}

      <section className='extraction-metrics' aria-label='Indicadores de extração'>
        <div className='metric-card'>
          <p className='metric-label'>TOTAL DE E-MAILS PROCESSADOS</p>
          <strong className='metric-value'>
            {status?.total_processed ?? 0}
          </strong>
        </div>

        <div className='metric-card'>
          <p className='metric-label'>ERROS</p>
          <strong className='metric-value'>
            {errorCount}
          </strong>
        </div>

        <div className='metric-card'>
          <p className='metric-label'>ÚLTIMA EXECUÇÃO</p>
          <strong className='metric-value metric-value-date'>
            {formatDateTime(status?.last_run_at)}
          </strong>
        </div>
      </section>

      <section className='recent-section'>
        <h2>Últimos processados</h2>

        {recentProcessed.length > 0 ? (
          <ul className='recent-list'>
            {recentProcessed.map((item) => (
              <li key={item.id} className='recent-item'>
                <strong>
                  {item.event_id
                    ? `Evento processado #${item.event_id}`
                    : `Extração #${item.id}`}
                </strong>
                <p>
                  {formatDateTime(item.created_at)}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p>Nenhum e-mail processado recentemente.</p>
        )}
      </section>

      <section className='alerts-section'>
        <h2>Alertas</h2>

        {alerts.length > 0 ? (
          <ul className='recent-list'>
            {alerts.map((alert) => (
              <li key={alert.id} className='recent-item'>
                <strong>
                  {alert.error_message || 'Extração não concluída'}
                </strong>
                <p>
                  {formatDateTime(alert.created_at)}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p>Nenhum alerta.</p>
        )}
      </section>
    </main>
  );
}
