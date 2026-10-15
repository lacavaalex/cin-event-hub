-- =====================================================================
-- Testes do database/001_schema.sql (PostgreSQL 13+)
-- Jeito recomendado (cria um banco temporário e apaga no fim):
--   python database/run_tests.py
-- Manual, em um banco DESCARTÁVEL que já recebeu o 001_schema.sql:
--   psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/tests/001_schema_test.sql
-- Cada verificação mostra "ok: ..." ou para com "FALHOU: ...".
-- Os testes deixam dados no banco: não rode em um banco com dados de verdade.
-- =====================================================================

-- Ajudantes temporários (somem quando a conexão fecha).
CREATE OR REPLACE FUNCTION pg_temp.verificar(descricao text, condicao boolean) RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
    IF condicao IS NOT TRUE THEN
        RAISE EXCEPTION 'FALHOU: %', descricao;
    END IF;
    RAISE NOTICE 'ok: %', descricao;
END $$;

-- O comando precisa ser aceito pelo banco.
CREATE OR REPLACE FUNCTION pg_temp.deve_inserir(descricao text, comando text) RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
    EXECUTE comando;
    RAISE NOTICE 'ok: %', descricao;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'FALHOU (deveria ser aceito): % -> %', descricao, SQLERRM;
END $$;

-- O comando precisa ser rejeitado por uma restrição específica.
-- restricao = NULL aceita qualquer violação de integridade (ex.: NOT NULL).
CREATE OR REPLACE FUNCTION pg_temp.deve_falhar(descricao text, comando text, restricao text) RETURNS void
LANGUAGE plpgsql AS $$
DECLARE
    violada text;
BEGIN
    BEGIN
        EXECUTE comando;
    EXCEPTION WHEN integrity_constraint_violation THEN
        GET STACKED DIAGNOSTICS violada = CONSTRAINT_NAME;
        IF restricao IS NOT NULL AND violada IS DISTINCT FROM restricao THEN
            RAISE EXCEPTION 'FALHOU: % -> rejeitado pela restrição "%" em vez de "%"',
                            descricao, violada, restricao;
        END IF;
        RAISE NOTICE 'ok: %', descricao;
        RETURN;
    END;
    RAISE EXCEPTION 'FALHOU: % -> o comando deveria ser rejeitado', descricao;
END $$;

-- Dados de apoio: um admin, um aluno e duas extrações.
INSERT INTO users (name, email, hashed_password, is_admin)
VALUES ('Admin', 'admin@cin.ufpe.br', 'x', TRUE), ('Aluno', 'aluno@cin.ufpe.br', 'x', FALSE);
INSERT INTO extractions (message_id, body_hash, status)
VALUES ('m1', 'h1', 'processed'), ('m2', 'h2', 'duplicate');

-- ---------------------------------------------------------------------
-- events: o que deve ser aceito
-- ---------------------------------------------------------------------
SELECT pg_temp.deve_inserir('evento manual válido, cadastrado por um admin', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link, admin_id)
    VALUES ('Evento A', 'd', 'Palestra', '2026-12-01', '10:00', 'CIn', 'https://x.com',
            (SELECT id FROM users WHERE email = 'admin@cin.ufpe.br'))$q$);
SELECT pg_temp.deve_inserir('mesmo título em outra data', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('Evento A', 'd', 'Palestra', '2026-12-02', '11:00', 'CIn', 'https://x.com')$q$);
SELECT pg_temp.deve_inserir('evento com fim no dia seguinte e capacidade', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link,
                        end_date, end_time, capacity)
    VALUES ('Hackathon X', 'd', 'Hackathon', '2026-12-05', '10:00', 'CIn', 'https://x.com',
            '2026-12-06', '10:00', 50)$q$);
SELECT pg_temp.deve_inserir('evento vindo de e-mail, ligado a uma extração', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link,
                        extraction_id, origin)
    VALUES ('Evento J', 'd', 'Workshop', '2026-12-07', '10:00', 'CIn', 'https://x.com',
            (SELECT id FROM extractions WHERE message_id = 'm1'), 'email')$q$);

-- ---------------------------------------------------------------------
-- events: o que deve ser rejeitado (e por qual restrição)
-- ---------------------------------------------------------------------
SELECT pg_temp.deve_falhar('título só com espaços', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('   ', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_title_preenchido');
SELECT pg_temp.deve_falhar('descrição vazia', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('B', '', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_description_preenchida');
SELECT pg_temp.deve_falhar('local só com espaços', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', '  ', 'https://x.com')$q$,
    'ck_events_location_preenchido');
SELECT pg_temp.deve_falhar('link de inscrição sem http(s)', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'x.com')$q$,
    'ck_events_registration_link_http');
SELECT pg_temp.deve_falhar('tipo de evento inválido', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link)
    VALUES ('B', 'd', 'Seminario', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_event_type');
SELECT pg_temp.deve_falhar('status do evento inválido', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link, status)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 'rascunho')$q$,
    'ck_events_status');
SELECT pg_temp.deve_falhar('capacidade zero', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link, capacity)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 0)$q$,
    'ck_events_capacity');
SELECT pg_temp.deve_falhar('fim antes do início', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link,
                        end_date, end_time)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', '2026-12-10', '09:00')$q$,
    'ck_events_fim_apos_inicio');
SELECT pg_temp.deve_falhar('end_date sem end_time', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link, end_date)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', '2026-12-11')$q$,
    'ck_events_fim_completo');
SELECT pg_temp.deve_falhar('extração inexistente', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link,
                        extraction_id, origin)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 999999, 'email')$q$,
    'fk_events_extraction');
SELECT pg_temp.deve_falhar('admin (usuário) inexistente', $q$
    INSERT INTO events (title, description, event_type, date, time, location, registration_link, admin_id)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 999999)$q$,
    'fk_events_admin');
SELECT pg_temp.deve_falhar('evento sem data', $q$
    INSERT INTO events (title, description, event_type, time, location, registration_link)
    VALUES ('B', 'd', 'Palestra', '10:00', 'CIn', 'https://x.com')$q$,
    NULL);

-- ---------------------------------------------------------------------
-- extractions e users
-- ---------------------------------------------------------------------
SELECT pg_temp.deve_falhar('message_id repetido em extractions', $q$
    INSERT INTO extractions (message_id, body_hash) VALUES ('m1', 'h9')$q$,
    'uq_extractions_message_id');
SELECT pg_temp.deve_falhar('e-mail de usuário repetido', $q$
    INSERT INTO users (name, email, hashed_password) VALUES ('Outro', 'aluno@cin.ufpe.br', 'x')$q$,
    'uq_users_email');

-- ---------------------------------------------------------------------
-- Comportamentos: exclusões
-- ---------------------------------------------------------------------
DELETE FROM users WHERE email = 'admin@cin.ufpe.br';
SELECT pg_temp.verificar('apagar o admin mantém o evento, com admin_id nulo',
    (SELECT admin_id IS NULL FROM events
     WHERE title = 'Evento A' AND date = '2026-12-01'));

DELETE FROM extractions WHERE message_id = 'm1';
SELECT pg_temp.verificar('apagar a extração mantém o evento, com extraction_id nulo',
    (SELECT extraction_id IS NULL FROM events WHERE title = 'Evento J'));
