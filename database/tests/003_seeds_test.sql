-- =====================================================================
-- Testes dos seeds 003_seed_usuarios, 004_seed_extracoes e 005_seed_favoritos
-- (PostgreSQL 13+)
-- Jeito recomendado (cria um banco temporário e apaga no fim):
--   python database/run_tests.py
-- Manual, em um banco DESCARTÁVEL que já recebeu o 001_schema.sql e os seeds
-- 002 a 005, nessa ordem:
--   psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/tests/003_seeds_test.sql
-- Cada verificação mostra "ok: ..." ou para com "FALHOU: ...".
-- O run_tests.py roda este arquivo duas vezes: depois dos seeds e depois de
-- repeti-los. Os mesmos números nas duas vezes provam que nada duplica.
-- =====================================================================

CREATE OR REPLACE FUNCTION pg_temp.verificar(descricao text, condicao boolean) RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
    IF condicao IS NOT TRUE THEN
        RAISE EXCEPTION 'FALHOU: %', descricao;
    END IF;
    RAISE NOTICE 'ok: %', descricao;
END $$;

-- ---------------------------------------------------------------------
-- usuario
-- ---------------------------------------------------------------------
SELECT pg_temp.verificar('5 usuários: 2 administradores e 3 comuns',
    (SELECT count(*) FROM usuario) = 5
    AND (SELECT count(*) FROM usuario WHERE is_admin) = 2
    AND (SELECT count(*) FROM usuario WHERE NOT is_admin) = 3);
SELECT pg_temp.verificar('todos os e-mails dos usuários são de example.com',
    (SELECT bool_and(email LIKE '%@example.com') FROM usuario));
SELECT pg_temp.verificar('datas de cadastro nos últimos 90 dias e nunca no futuro',
    (SELECT bool_and(dt_cadastro <= CURRENT_DATE AND dt_cadastro >= CURRENT_DATE - 90) FROM usuario));
SELECT pg_temp.verificar('há nome com acento e nome com mais de 40 caracteres',
    (SELECT count(*) FROM usuario WHERE nome LIKE '%ú%') >= 1
    AND (SELECT max(length(nome)) FROM usuario) > 40);

-- ---------------------------------------------------------------------
-- extracao
-- ---------------------------------------------------------------------
SELECT pg_temp.verificar('7 extrações seed, e os 6 status do CHECK aparecem',
    (SELECT count(*) FROM extracao WHERE gmail_message_id LIKE 'seed-msg-%') = 7
    AND (SELECT count(DISTINCT status) FROM extracao) = 6);
SELECT pg_temp.verificar('2 processado, 1 processado_ia e 1 de cada um dos outros status',
    (SELECT count(*) FROM extracao WHERE status = 'processado') = 2
    AND (SELECT count(*) FROM extracao WHERE status = 'processado_ia') = 1
    AND (SELECT count(*) FROM extracao WHERE status IN ('ignorado', 'nao_processado', 'extracao_incompleta', 'erro')) = 4);
SELECT pg_temp.verificar('só processado e processado_ia têm event_id, e o evento é de origem email',
    (SELECT bool_and((status IN ('processado', 'processado_ia')) = (event_id IS NOT NULL)) FROM extracao)
    AND (SELECT count(*) FROM extracao x JOIN events e ON e.id_event = x.event_id
         WHERE e.origin = 'email') = 3);
SELECT pg_temp.verificar('3 eventos de e-mail, ativos e no futuro, um deles sem link de inscrição',
    (SELECT count(*) FROM events WHERE origin = 'email') = 3
    AND (SELECT bool_and(status = 'active' AND int_event_date > CURRENT_DATE) FROM events WHERE origin = 'email')
    AND (SELECT count(*) FROM events WHERE origin = 'email' AND registration_link = '') = 1);
SELECT pg_temp.verificar('o seed de eventos manuais continua com 20 eventos',
    (SELECT count(*) FROM events WHERE origin = 'manual') = 20);
SELECT pg_temp.verificar('source_email só guarda domínio (sem endereço de pessoa)',
    (SELECT bool_and(position('@' IN source_email) = 0) FROM extracao));
SELECT pg_temp.verificar('extracted_data é objeto JSON quando preenchido; erro e ignorado têm mensagem',
    (SELECT bool_and(json_typeof(extracted_data) = 'object') FROM extracao WHERE extracted_data IS NOT NULL)
    AND (SELECT bool_and(error_message IS NOT NULL) FROM extracao WHERE status IN ('erro', 'ignorado')));
SELECT pg_temp.verificar('datas de criação das extrações nunca estão no futuro',
    (SELECT bool_and(created_at <= now()) FROM extracao));

-- ---------------------------------------------------------------------
-- favorito
-- ---------------------------------------------------------------------
SELECT pg_temp.verificar('8 favoritos, todos de usuários e eventos que existem',
    (SELECT count(*) FROM favorito) = 8
    AND (SELECT count(*) FROM favorito f
         JOIN usuario u ON u.id_usuario = f.id_usuario
         JOIN events e ON e.id_event = f.id_events) = 8);
SELECT pg_temp.verificar('Marina tem 3 favoritos, Pedro e Júlia 2, Ana 1 e Carlos nenhum',
    (SELECT count(*) FROM favorito f JOIN usuario u USING (id_usuario) WHERE u.email = 'marina.souza@example.com') = 3
    AND (SELECT count(*) FROM favorito f JOIN usuario u USING (id_usuario) WHERE u.email = 'pedro.costa@example.com') = 2
    AND (SELECT count(*) FROM favorito f JOIN usuario u USING (id_usuario) WHERE u.email = 'julia.fernandes@example.com') = 2
    AND (SELECT count(*) FROM favorito f JOIN usuario u USING (id_usuario) WHERE u.email = 'ana.lima@example.com') = 1
    AND (SELECT count(*) FROM favorito f JOIN usuario u USING (id_usuario) WHERE u.email = 'carlos.silva@example.com') = 0);
SELECT pg_temp.verificar('um evento favoritado por 2 usuários e favoritos em eventos de e-mail',
    (SELECT max(c) FROM (SELECT count(*) AS c FROM favorito GROUP BY id_events) d) = 2
    AND (SELECT count(*) FROM favorito f JOIN events e ON e.id_event = f.id_events WHERE e.origin = 'email') = 2);
