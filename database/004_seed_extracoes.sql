-- =====================================================================
-- Massa de dados fictícia (6 extrações de e-mail, uma por status, e os 3 eventos
-- que elas publicaram)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com extrações reais.
-- Pré-requisito: database/001_schema.sql já executado (PostgreSQL).
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/004_seed_extracoes.sql
--
-- Primeiro cria 3 eventos com origin 'email' (o 002_seed_eventos.sql só tem eventos
-- manuais), depois as extrações, ligando cada uma ao evento que gerou pelo título.
-- Os gmail_message_id começam com "seed-" para ficarem fáceis de identificar.
-- source_email guarda só o domínio do remetente (sem endereço de pessoa, por LGPD).
-- extracted_data é um objeto JSON com os campos extraídos, sem datas, para não
-- ficar defasado com o tempo. created_at e as datas dos eventos são relativas ao
-- momento da execução.
-- Pode rodar mais de uma vez: evento com o mesmo título e extração com o mesmo
-- gmail_message_id não são inseridos de novo.
-- Para recomeçar do zero:
--   DELETE FROM extracao WHERE gmail_message_id LIKE 'seed-msg-%';
--   DELETE FROM events WHERE title IN ('Seminário de Visão Computacional Aplicada',
--       'Oficina de Prompt Engineering com Gemini', 'Minicurso de SQL para Análise de Dados');
--
-- Casos úteis para testar as telas e o pipeline (os 6 status do CHECK):
--   * processado: 2 (parser), um deles com evento sem link de inscrição
--   * processado_ia: 1 (Gemini publicou o evento)
--   * ignorado, nao_processado, extracao_incompleta e erro: 1 de cada, sem evento
--   * só os status processado e processado_ia têm event_id
-- =====================================================================

INSERT INTO events (title, description, int_event_date, int_event_time, event_location,
                    event_type, registration_link, capacity, origin)
SELECT v.title,
       v.description,
       CURRENT_DATE + v.dias,
       v.hora::time,
       v.location,
       v.event_type,
       v.link,
       v.capacity::int,
       'email'
FROM (VALUES
    ('Seminário de Visão Computacional Aplicada',
     'Pesquisadores do CIn apresentam aplicações de visão computacional em saúde, agricultura e mobilidade.',
     12, '15:00', 'Auditório do CIn', 'Palestra', '', NULL),
    ('Oficina de Prompt Engineering com Gemini',
     'Oficina prática de escrita de prompts, avaliação de respostas e uso de saídas estruturadas em JSON.',
     16, '14:00', 'Laboratório de Graduação 4', 'Workshop',
     'https://example.com/inscricao/prompt-gemini', 25),
    ('Minicurso de SQL para Análise de Dados',
     'Consultas com JOIN, agregações e subconsultas sobre um banco de eventos acadêmicos.',
     20, '09:00', 'Laboratório de Graduação 2', 'Workshop',
     'https://example.com/inscricao/sql-analise', 30)
) AS v (title, description, dias, hora, location, event_type, link, capacity)
WHERE NOT EXISTS (SELECT 1 FROM events e WHERE e.title = v.title);

INSERT INTO extracao (gmail_message_id, source_email, status, extracted_data,
                      error_message, event_id, created_at)
SELECT v.gmail_message_id,
       v.source_email,
       v.status,
       v.extracted_data::json,
       v.error_message,
       e.id_event,
       now() - v.horas_atras * INTERVAL '1 hour'
FROM (VALUES
    ('seed-msg-0001', 'cin.ufpe.br', 'processado',
     '{"title": "Seminário de Visão Computacional Aplicada", "event_type": "Palestra", "time": "15:00", "location": "Auditório do CIn", "registration_link": ""}',
     NULL, 'Seminário de Visão Computacional Aplicada', 72),
    ('seed-msg-0002', 'cin.ufpe.br', 'processado',
     '{"title": "Minicurso de SQL para Análise de Dados", "event_type": "Workshop", "time": "09:00", "location": "Laboratório de Graduação 2", "registration_link": "https://example.com/inscricao/sql-analise", "capacity": 30}',
     NULL, 'Minicurso de SQL para Análise de Dados', 48),
    ('seed-msg-0003', 'listas.cin.ufpe.br', 'processado_ia',
     '{"title": "Oficina de Prompt Engineering com Gemini", "event_type": "Workshop", "time": "14:00", "location": "Laboratório de Graduação 4", "registration_link": "https://example.com/inscricao/prompt-gemini", "capacity": 25}',
     NULL, 'Oficina de Prompt Engineering com Gemini', 36),
    ('seed-msg-0004', 'cin.ufpe.br', 'ignorado',
     NULL,
     'e-mail sem dados obrigatórios: date, time', NULL, 24),
    ('seed-msg-0005', 'listas.cin.ufpe.br', 'nao_processado',
     NULL,
     'IA não retornou JSON válido (registro legado anterior à validação)', NULL, 12),
    ('seed-msg-0006', 'cin.ufpe.br', 'extracao_incompleta',
     '{"title": "Hackathon sem data", "event_type": "Hackathon", "location": "Centro de Informática"}',
     'evento descartado pela validação: data vazia', NULL, 6),
    ('seed-msg-0007', 'cin.ufpe.br', 'erro',
     NULL,
     'falha ao consultar a IA: tempo limite excedido', NULL, 1)
) AS v (gmail_message_id, source_email, status, extracted_data, error_message, titulo_evento, horas_atras)
LEFT JOIN events e ON e.title = v.titulo_evento
WHERE NOT EXISTS (SELECT 1 FROM extracao x WHERE x.gmail_message_id = v.gmail_message_id);
