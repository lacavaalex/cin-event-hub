-- =====================================================================
-- Testes do database/001_schema.sql (PostgreSQL 13+)
-- Tabelas testadas: usuario, extracao, events, favorito, email_associado.
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
-- (body_hash precisa ter exatamente 64 caracteres: repeat('a', 64).)
INSERT INTO usuario (nome, email, senha_hash, nome_perfil, is_admin)
VALUES ('Admin', 'admin@cin.ufpe.br', 'x', 'admin', TRUE),
       ('Aluno', 'aluno@cin.ufpe.br', 'x', 'aluno', FALSE);
INSERT INTO extracao (message_id, thread_id, body_hash, prompt, status)
VALUES ('m1', 't1', repeat('a', 64), 'p', 'success'),
       ('m2', 't2', repeat('b', 64), 'p', 'failed');

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
SELECT pg_temp.deve_inserir('extração válida com JSON de saída', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt, json_output)
    VALUES ('m3', 't3', repeat('c', 64), 'p', '{"title": "Evento"}')$q$);
SELECT pg_temp.verificar('status padrão da extração é pending e extracted_at é preenchido',
    (SELECT status = 'pending' AND extracted_at IS NOT NULL
     FROM extracao WHERE message_id = 'm3'));
SELECT pg_temp.deve_falhar('status de extração inválido', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt, status)
    VALUES ('m4', 't4', repeat('d', 64), 'p', 'processed')$q$,
    'extracao_status_check');
SELECT pg_temp.deve_falhar('message_id vazio', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt)
    VALUES (' ', 't5', repeat('e', 64), 'p')$q$,
    'ck_extracao_message_id_preenchido');
SELECT pg_temp.deve_falhar('thread_id vazio', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt)
    VALUES ('m6', '', repeat('e', 64), 'p')$q$,
    'ck_extracao_thread_id_preenchido');
SELECT pg_temp.deve_falhar('body_hash com tamanho diferente de 64', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt)
    VALUES ('m7', 't7', 'curto', 'p')$q$,
    'ck_extracao_body_hash_valido');
SELECT pg_temp.deve_falhar('prompt vazio', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt)
    VALUES ('m8', 't8', repeat('e', 64), '  ')$q$,
    'ck_extracao_prompt_preenchido');
SELECT pg_temp.deve_falhar('extração sem thread_id (NOT NULL)', $q$
    INSERT INTO extracao (message_id, body_hash, prompt)
    VALUES ('m9', repeat('e', 64), 'p')$q$,
    NULL);
-- índice único parcial sucesso_de_extracao: só 1 extração "success" por (message_id, thread_id)
SELECT pg_temp.deve_falhar('segunda extração com sucesso para a mesma mensagem e thread', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt, status)
    VALUES ('m1', 't1', repeat('a', 64), 'p', 'success')$q$,
    'sucesso_de_extracao');
SELECT pg_temp.deve_inserir('mesma mensagem e thread com status failed ou pending não conflita', $q$
    INSERT INTO extracao (message_id, thread_id, body_hash, prompt, status)
    VALUES ('m1', 't1', repeat('a', 64), 'p', 'failed'),
           ('m1', 't1', repeat('a', 64), 'p', 'pending')$q$);

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
SELECT pg_temp.deve_inserir('evento vindo de e-mail, ligado a uma extração', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link, extraction_id, origin)
    VALUES ('Evento J', 'd', 'Workshop', '2026-12-07', '10:00', 'CIn', 'https://x.com',
            (SELECT id_extracao FROM extracao WHERE message_id = 'm1' AND status = 'success'), 'email')$q$);
SELECT pg_temp.deve_inserir('os quatro tipos de evento são aceitos', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time,
                        event_location, registration_link)
    VALUES ('T1', 'd', 'Palestra', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T2', 'd', 'Workshop', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T3', 'd', 'Hackathon', '2026-12-02', '10:00', 'CIn', 'https://x.com'),
           ('T4', 'd', 'Outro', '2026-12-02', '10:00', 'CIn', 'https://x.com')$q$);
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
SELECT pg_temp.deve_falhar('extração inexistente', $q$
    INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link,
                        extraction_id, origin)
    VALUES ('B', 'd', 'Palestra', '2026-12-10', '10:00', 'CIn', 'https://x.com', 999999, 'email')$q$,
    'fk_events_extracao');
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
-- email_associado
-- =====================================================================
SELECT pg_temp.deve_inserir('e-mail (extração) associado a um evento', $q$
    INSERT INTO email_associado (id_extracao, id_evento)
    VALUES ((SELECT id_extracao FROM extracao WHERE message_id = 'm1' AND status = 'success'),
            (SELECT id_event FROM events WHERE title = 'Evento J'))$q$);
SELECT pg_temp.deve_falhar('mesma associação duas vezes', $q$
    INSERT INTO email_associado (id_extracao, id_evento)
    VALUES ((SELECT id_extracao FROM extracao WHERE message_id = 'm1' AND status = 'success'),
            (SELECT id_event FROM events WHERE title = 'Evento J'))$q$,
    'pk_email_associado');
SELECT pg_temp.deve_falhar('associação com extração inexistente', $q$
    INSERT INTO email_associado (id_extracao, id_evento)
    VALUES (999999, (SELECT id_event FROM events WHERE title = 'Evento J'))$q$,
    'fk_email_associado_extracao');
SELECT pg_temp.deve_falhar('associação com evento inexistente', $q$
    INSERT INTO email_associado (id_extracao, id_evento)
    VALUES ((SELECT id_extracao FROM extracao WHERE message_id = 'm1' AND status = 'success'), 999999)$q$,
    'fk_email_associado_events');

-- =====================================================================
-- Comportamentos: exclusões (ON DELETE)
-- =====================================================================
-- favorito e email_associado somem junto com o evento (CASCADE)
INSERT INTO events (title, description, event_type, int_event_date, int_event_time, event_location, registration_link)
VALUES ('Evento para apagar', 'd', 'Outro', '2026-12-20', '10:00', 'CIn', 'https://x.com');
INSERT INTO favorito (id_usuario, id_events)
SELECT (SELECT id_usuario FROM usuario WHERE email = 'maria@cin.ufpe.br'), id_event
FROM events WHERE title = 'Evento para apagar';
INSERT INTO email_associado (id_extracao, id_evento)
SELECT (SELECT id_extracao FROM extracao WHERE message_id = 'm2'), id_event
FROM events WHERE title = 'Evento para apagar';
DELETE FROM events WHERE title = 'Evento para apagar';
SELECT pg_temp.verificar('apagar o evento apaga os favoritos e as associações dele',
    (SELECT count(*) FROM favorito f JOIN usuario u ON u.id_usuario = f.id_usuario
     WHERE u.email = 'maria@cin.ufpe.br') = 0
    AND (SELECT count(*) FROM email_associado a JOIN extracao x ON x.id_extracao = a.id_extracao
         WHERE x.message_id = 'm2') = 0);

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

-- apagar a extração mantém o evento, com extraction_id nulo, e some das associações
DELETE FROM extracao WHERE message_id = 'm1' AND status = 'success';
SELECT pg_temp.verificar('apagar a extração mantém o evento, com extraction_id nulo',
    (SELECT extraction_id IS NULL FROM events WHERE title = 'Evento J'));
SELECT pg_temp.verificar('apagar a extração remove a associação com o evento',
    (SELECT count(*) FROM email_associado) = 0);
