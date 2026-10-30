-- =====================================================================
-- Massa de dados fictícia (5 extrações de e-mail)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com extrações reais.
-- Pré-requisito: database/001_schema.sql já executado (PostgreSQL).
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/004_seed_extracoes.sql
--
-- Os message_id e thread_id começam com "seed-" para ficarem fáceis de identificar.
-- body_hash é um SHA-256 (64 caracteres hexadecimais), como exige o CHECK.
-- extracted_at é relativa ao momento da execução (agora - N horas).
-- json_output traz os campos que a extração produziria, sem datas, para não
-- ficar defasado com o tempo.
-- Pode rodar mais de uma vez: uma extração cujo message_id e thread_id já existem
-- não é inserida de novo.
-- Para recomeçar do zero: DELETE FROM extracao WHERE message_id LIKE 'seed-msg-%';
--   (os vínculos em email_associado somem em cascata; eventos ligados a elas
--   ficam com extraction_id NULL)
--
-- Casos úteis para testar as telas e o pipeline:
--   * 3 extrações com status 'success' (cada uma vira um evento em email_associado)
--   * 1 extração 'failed' com mensagem de erro e sem json_output
--   * 1 extração 'pending' ainda sem texto de entrada
--   * a regra do índice único: só uma extração 'success' por message_id + thread_id
-- =====================================================================

INSERT INTO extracao (message_id, thread_id, body_hash, input_text, prompt,
                      json_output, status, error_message, extracted_at)
SELECT v.message_id,
       v.thread_id,
       encode(sha256(convert_to('corpo do email ' || v.message_id, 'UTF8')), 'hex'),
       v.input_text,
       'Extraia título, descrição, tipo, data, hora, local e link de inscrição do e-mail.',
       v.json_output::jsonb,
       v.status,
       v.error_message,
       now() - v.horas_atras * INTERVAL '1 hour'
FROM (VALUES
    ('seed-msg-0001', 'seed-thread-0001',
     'Workshop de Git e GitHub para Iniciantes. Amanhã, das 14h às 17h, no Laboratório de Graduação 2. São 30 vagas. Inscrições: https://example.com/inscricao/git-github',
     '{"title": "Workshop de Git e GitHub para Iniciantes", "event_type": "Workshop", "time": "14:00", "end_time": "17:00", "location": "Laboratório de Graduação 2", "registration_link": "https://example.com/inscricao/git-github", "capacity": 30}',
     'success', NULL, 72),
    ('seed-msg-0002', 'seed-thread-0002',
     'Oficina prática de Python para Análise de Dados, das 13h30 às 17h30, no Laboratório de Graduação 3. Vagas: 30. Link: https://example.com/inscricao/python-dados',
     '{"title": "Python para Análise de Dados", "event_type": "Workshop", "time": "13:30", "end_time": "17:30", "location": "Laboratório de Graduação 3", "registration_link": "https://example.com/inscricao/python-dados", "capacity": 30}',
     'success', NULL, 48),
    ('seed-msg-0003', 'seed-thread-0003',
     'Hackathon de Saúde Digital: 24 horas de desenvolvimento no Centro de Informática, começando às 9h. 100 vagas. Inscrições: https://example.com/inscricao/hackathon-saude',
     '{"title": "Hackathon de Saúde Digital", "event_type": "Hackathon", "time": "09:00", "end_time": "09:00", "location": "Centro de Informática", "registration_link": "https://example.com/inscricao/hackathon-saude", "capacity": 100}',
     'success', NULL, 24),
    ('seed-msg-0004', 'seed-thread-0004',
     'Boletim semanal do CIn com avisos gerais, sem divulgação de nenhum evento específico.',
     NULL,
     'failed', 'Nenhum evento identificado no corpo do e-mail.', 12),
    ('seed-msg-0005', 'seed-thread-0005',
     NULL,
     NULL,
     'pending', NULL, 1)
) AS v (message_id, thread_id, input_text, json_output, status, error_message, horas_atras)
WHERE NOT EXISTS (SELECT 1 FROM extracao x
                  WHERE x.message_id = v.message_id AND x.thread_id = v.thread_id);
