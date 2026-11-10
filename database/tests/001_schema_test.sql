-- =====================================================================
-- Testes do database/001_schema.sql (PostgreSQL 13+)
-- Tabelas testadas: usuario, extracao, events, favorito.
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

-- Dados de apoio: um admin, um aluno e duas extrações (uma ignorada, uma com erro).
INSERT INTO usuario (nome, email, senha_hash, nome_perfil, is_admin)
VALUES ('Admin', 'admin@cin.ufpe.br', 'x', 'admin', TRUE),
       ('Aluno', 'aluno@cin.ufpe.br', 'x', 'aluno', FALSE);
INSERT INTO extracao (gmail_message_id, source_email, status, error_message)
VALUES ('m1', 'sec@cin.ufpe.br', 'ignorado', 'e-mail sem dados obrigatórios: date'),
       ('m2', 'sec@cin.ufpe.br', 'erro', 'falha de rede');

-- =====================================================================
-- usuario
-- =====================================================================
SELECT pg_temp.deve_inserir('usuário aluno válido', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('Maria', 'maria@cin.ufpe.br', 'hash', 'maria')$q$);
SELECT pg_temp.verificar('valores padrão do usuário: não é admin e data de cadastro é hoje',
    (SELECT is_admin = FALSE AND dt_cadastro = CURRENT_DATE
     FROM usuario WHERE email = 'maria@cin.ufpe.br'));
SELECT pg_temp.deve_falhar('e-mail de usuário repetido', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('Outro', 'aluno@cin.ufpe.br', 'x', 'outro')$q$,
    'uk_usuario_email');
SELECT pg_temp.deve_falhar('nome só com espaços', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('   ', 'a1@cin.ufpe.br', 'x', 'p')$q$,
    'ck_usuario_nome_preenchido');
SELECT pg_temp.deve_falhar('e-mail vazio', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('N', '', 'x', 'p')$q$,
    'ck_usuario_email_preenchido');
SELECT pg_temp.deve_falhar('senha_hash vazia', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('N', 'a2@cin.ufpe.br', ' ', 'p')$q$,
    'ck_usuario_senha_hash_preenchida');
SELECT pg_temp.deve_falhar('nome_perfil vazio', $q$
    INSERT INTO usuario (nome, email, senha_hash, nome_perfil)
    VALUES ('N', 'a3@cin.ufpe.br', 'x', '')$q$,
    'ck_usuario_nome_perfil_preenchido');
SELECT pg_temp.deve_falhar('usuário sem nome_perfil (NOT NULL)', $q$
    INSERT INTO usuario (nome, email, senha_hash) VALUES ('N', 'a4@cin.ufpe.br', 'x')$q$,
    NULL);

-- =====================================================================
-- extracao
-- =====================================================================
SELECT pg_temp.deve_inserir('extração ignorada, sem evento e sem dados extraídos', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status, error_message)
    VALUES ('m3', 'sec@cin.ufpe.br', 'ignorado', 'e-mail sem dados obrigatórios: time')$q$);
SELECT pg_temp.verificar('created_at da extração é preenchido e event_id fica nulo',
    (SELECT created_at IS NOT NULL AND event_id IS NULL
     FROM extracao WHERE gmail_message_id = 'm3'));
SELECT pg_temp.deve_inserir('remetente vazio é aceito (o Gmail pode não mandar o From)', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status)
    VALUES ('m4', '', 'erro')$q$);
SELECT pg_temp.deve_falhar('status de extração inválido', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status)
    VALUES ('m5', 'sec@cin.ufpe.br', 'success')$q$,
    'ck_extracao_status');
SELECT pg_temp.deve_falhar('gmail_message_id vazio', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status)
    VALUES (' ', 'sec@cin.ufpe.br', 'erro')$q$,
    'ck_extracao_gmail_message_id_preenchido');
SELECT pg_temp.deve_falhar('mesma mensagem do Gmail registrada duas vezes', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status)
    VALUES ('m1', 'sec@cin.ufpe.br', 'erro')$q$,
    'uk_extracao_gmail_message_id');
SELECT pg_temp.deve_falhar('extração sem status (NOT NULL)', $q$
    INSERT INTO extracao (gmail_message_id, source_email)
    VALUES ('m6', 'sec@cin.ufpe.br')$q$,
    NULL);
SELECT pg_temp.deve_falhar('extração sem remetente (NOT NULL)', $q$
    INSERT INTO extracao (gmail_message_id, status)
    VALUES ('m7', 'erro')$q$,
    NULL);

-- =====================================================================
-- events: o que deve ser aceito
-- =====================================================================
SELECT pg_temp.deve_inserir('evento manual válido, cadastrado por um admin', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, admin_id)
    VALUES ('Evento A', 'd', 'Palestra', '2026-12-01', '10:00', 'CIn', 'https://x.com',
            (SELECT id_usuario FROM usuario WHERE email = 'admin@cin.ufpe.br'))$q$);
SELECT pg_temp.verificar('valores padrão do evento: status active, origin manual e datas de criação preenchidas',
    (SELECT status = 'active' AND origin = 'manual'
            AND created_at IS NOT NULL AND updated_at IS NOT NULL
     FROM events WHERE title = 'Evento A'));
SELECT pg_temp.deve_inserir('mesmo título em outra data', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link)
    VALUES ('Evento A', 'd', 'Palestra', '2026-12-02', '11:00', 'CIn', 'https://x.com')$q$);
SELECT pg_temp.deve_inserir('evento com fim no dia seguinte e capacidade', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, end_event_date, end_event_time, capacity)
    VALUES ('Hackathon X', 'd', 'Hackathon', '2026-12-05', '10:00', 'CIn', 'https://x.com',
            '2026-12-06', '10:00', 50)$q$);
SELECT pg_temp.deve_inserir('evento vindo de e-mail', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, origin)
    VALUES ('Evento J', 'd', 'Workshop', '2026-12-07', '10:00', 'CIn', 'https://x.com', 'email')$q$);
SELECT pg_temp.deve_inserir('os quatro tipos de evento são aceitos', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link)
    VALUES ('T1', 'd', 'Palestra', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T2', 'd', 'Workshop', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T3', 'd', 'Hackathon', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T4', 'd', 'Outro', '2026-12-02', '10:00', 'CIn', 'https://x.com')$q$);
SELECT pg_temp.deve_inserir('evento de e-mail sem link (o parser pode não achar um — US 4.1)', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, origin)
    VALUES ('Evento K', 'd', 'Palestra', '2026-12-08', '10:00', 'CIn', '', 'email')$q$);
SELECT pg_temp.deve_inserir('status inactive é aceito', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, status)
    VALUES ('Inativo', 'd', 'Outro', '2026-12-02', '10:00', 'CIn', 'https://x.com', 'inactive')$q$);

-- =====================================================================
-- events: o que deve ser rejeitado (e por qual restrição)
-- =====================================================================
SELECT pg_temp.deve_falhar('título só com espaços', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('   ', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_title_preenchido');
SELECT pg_temp.deve_falhar('descrição vazia', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', '', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_description_preenchida');
SELECT pg_temp.deve_falhar('local só com espaços', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', '  ', 'https://x.com')$q$,
    'ck_events_location_preenchido');
SELECT pg_temp.deve_falhar('link de inscrição sem http(s)', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'x.com')$q$,
    'ck_events_registration_link_http');
SELECT pg_temp.deve_falhar('evento manual sem link de inscrição (vazio)', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', '')$q$,
    'ck_events_registration_link_http');
SELECT pg_temp.deve_falhar('evento de e-mail com link preenchido sem http(s)', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, origin)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'x.com', 'email')$q$,
    'ck_events_registration_link_http');
SELECT pg_temp.deve_falhar('tipo de evento inválido', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', 'd', 'Seminario', '2026-12-10', '10:00', 'CIn', 'https://x.com')$q$,
    'ck_events_event_type');
SELECT pg_temp.deve_falhar('status do evento inválido', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, status)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 'rascunho')$q$,
    'ck_events_status');
SELECT pg_temp.deve_falhar('capacidade zero', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, capacity)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 0)$q$,
    'ck_events_capacity');
SELECT pg_temp.deve_falhar('fim antes do início', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link,
                        end_event_date, end_event_time)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', '2026-12-10', '09:00')$q$,
    'ck_events_fim_apos_inicio');
SELECT pg_temp.deve_falhar('end_event_date sem end_event_time', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, end_event_date)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', '2026-12-11')$q$,
    'ck_events_fim_completo');
SELECT pg_temp.deve_falhar('admin (usuário) inexistente', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, admin_id)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 999999)$q$,
    'fk_events_usuario');
SELECT pg_temp.deve_falhar('evento sem data', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
    VALUES ('B', 'd', 'Palestra', NULL, '10:00', 'CIn', 'https://x.com')$q$,
    NULL);
SELECT pg_temp.deve_falhar('evento sem hora', $q$
    INSERT INTO events (title, description, event_type, int_event_date, event_location, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', 'CIn', 'https://x.com')$q$,
    NULL);
SELECT pg_temp.deve_falhar('evento sem local', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, registration_link)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'https://x.com')$q$,
    NULL);
SELECT pg_temp.deve_falhar('evento sem link de inscrição', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn')$q$,
    NULL);

-- =====================================================================
-- extracao x events: o log aponta para o evento que gerou
-- =====================================================================
SELECT pg_temp.deve_inserir('extração processada ligada ao evento que gerou', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status, extracted_data, event_id)
    VALUES ('m10', 'sec@cin.ufpe.br', 'processado', '{"title": "Evento J"}',
            (SELECT id_event FROM events WHERE title = 'Evento J'))$q$);
SELECT pg_temp.deve_falhar('extração ligada a evento inexistente', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status, event_id)
    VALUES ('m11', 'sec@cin.ufpe.br', 'processado', 999999)$q$,
    'fk_extracao_events');
SELECT pg_temp.deve_falhar('extração ignorada não pode apontar para evento', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status, event_id)
    VALUES ('m12', 'sec@cin.ufpe.br', 'ignorado',
            (SELECT id_event FROM events WHERE title = 'Evento J'))$q$,
    'ck_extracao_evento_so_processado');
SELECT pg_temp.deve_inserir('extração processada sem evento (evento já apagado)', $q$
    INSERT INTO extracao (gmail_message_id, source_email, status)
    VALUES ('m13', 'sec@cin.ufpe.br', 'processado')$q$);

-- =====================================================================
-- favorito
-- =====================================================================
SELECT pg_temp.deve_inserir('aluno favorita um evento', $q$
    INSERT INTO favorito (id_usuario, id_events)
    VALUES ((SELECT id_usuario FROM usuario WHERE email = 'aluno@cin.ufpe.br'),
            (SELECT id_event FROM events WHERE title = 'Hackathon X'))$q$);
SELECT pg_temp.deve_falhar('favoritar o mesmo evento duas vezes', $q$
    INSERT INTO favorito (id_usuario, id_events)
    VALUES ((SELECT id_usuario FROM usuario WHERE email = 'aluno@cin.ufpe.br'),
            (SELECT id_event FROM events WHERE title = 'Hackathon X'))$q$,
    'pk_favorito');
SELECT pg_temp.deve_falhar('favorito de usuário inexistente', $q$
    INSERT INTO favorito (id_usuario, id_events)
    VALUES (999999, (SELECT id_event FROM events WHERE title = 'Hackathon X'))$q$,
    'fk_favorito_usuario');
SELECT pg_temp.deve_falhar('favorito de evento inexistente', $q$
    INSERT INTO favorito (id_usuario, id_events)
    VALUES ((SELECT id_usuario FROM usuario WHERE email = 'aluno@cin.ufpe.br'), 999999)$q$,
    'fk_favorito_evento');

-- =====================================================================
-- Comportamentos: exclusões (ON DELETE)
-- =====================================================================
-- favorito some junto com o evento (CASCADE)
INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
VALUES ('Evento para apagar', 'd', 'Outro', '2026-12-20', '10:00', 'CIn', 'https://x.com');
INSERT INTO favorito (id_usuario, id_events)
SELECT (SELECT id_usuario FROM usuario WHERE email = 'maria@cin.ufpe.br'), id_event
FROM events WHERE title = 'Evento para apagar';
DELETE FROM events WHERE title = 'Evento para apagar';
SELECT pg_temp.verificar('apagar o evento apaga os favoritos dele',
    (SELECT count(*) FROM favorito f JOIN usuario u ON u.id_usuario = f.id_usuario
     WHERE u.email = 'maria@cin.ufpe.br') = 0);

-- apagar o usuário apaga os favoritos dele
DELETE FROM usuario WHERE email = 'aluno@cin.ufpe.br';
SELECT pg_temp.verificar('apagar o aluno apaga os favoritos dele e mantém o evento favoritado',
    (SELECT count(*) FROM favorito) = 0
    AND (SELECT count(*) FROM events WHERE title = 'Hackathon X') = 1);

-- apagar o admin mantém o evento, com admin_id nulo (SET NULL)
DELETE FROM usuario WHERE email = 'admin@cin.ufpe.br';
SELECT pg_temp.verificar('apagar o admin mantém o evento, com admin_id nulo',
    (SELECT admin_id IS NULL FROM events
     WHERE title = 'Evento A' AND int_event_date = '2026-12-01'));

-- apagar o evento mantém o log de extração, com event_id nulo (SET NULL)
INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link, origin)
VALUES ('Evento de e-mail para apagar', 'd', 'Outro', '2026-12-21', '10:00', 'CIn', 'https://x.com', 'email');
INSERT INTO extracao (gmail_message_id, source_email, status, event_id)
SELECT 'm20', 'sec@cin.ufpe.br', 'processado', id_event
FROM events WHERE title = 'Evento de e-mail para apagar';
DELETE FROM events WHERE title = 'Evento de e-mail para apagar';
SELECT pg_temp.verificar('apagar o evento mantém o log de extração, com event_id nulo',
    (SELECT event_id IS NULL AND status = 'processado' FROM extracao WHERE gmail_message_id = 'm20'));

-- apagar a extração mantém o evento
DELETE FROM extracao WHERE gmail_message_id = 'm10';
SELECT pg_temp.verificar('apagar a extração mantém o evento gerado por ela',
    (SELECT count(*) FROM events WHERE title = 'Evento J') = 1);
