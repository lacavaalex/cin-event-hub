-- =====================================================================
-- Massa de dados fictícia (3 vínculos entre extração e evento)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com dados reais.
-- Pré-requisitos (PostgreSQL), nesta ordem:
--   database/001_schema.sql, 002_seed_eventos.sql e 004_seed_extracoes.sql
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/006_seed_emails_associados.sql
--
-- Cada vínculo liga uma extração com status 'success' ao evento que ela gerou.
-- Os vínculos são resolvidos por message_id e título do evento, porque os ids
-- são gerados automaticamente (GENERATED ALWAYS AS IDENTITY).
-- As extrações 'failed' e 'pending' ficam de fora de propósito: não geraram evento.
-- Se a extração ou o evento não existir, a linha é ignorada em silêncio: confira
-- com SELECT count(*) FROM email_associado; (esperado: 3).
-- Pode rodar mais de uma vez: um vínculo que já existe não é inserido de novo.
-- Para recomeçar do zero: TRUNCATE email_associado;
--
-- Casos úteis para testar as telas:
--   * eventos de tipos diferentes (2 Workshops e 1 Hackathon) com e-mail de origem
--   * eventos sem e-mail associado (os demais da massa de eventos)
-- =====================================================================

INSERT INTO email_associado (id_extracao, id_evento)
SELECT x.id_extracao, e.id_event
FROM (VALUES
    ('seed-msg-0001', 'Workshop de Git e GitHub para Iniciantes'),
    ('seed-msg-0002', 'Python para Análise de Dados'),
    ('seed-msg-0003', 'Hackathon de Saúde Digital')
) AS v (message_id, titulo)
JOIN extracao x ON x.message_id = v.message_id AND x.status = 'success'
JOIN events   e ON e.title = v.titulo
WHERE NOT EXISTS (SELECT 1 FROM email_associado a
                  WHERE a.id_extracao = x.id_extracao AND a.id_evento = e.id_event);
