-- =====================================================================
-- Testes do database/002_seed_eventos.sql (PostgreSQL 13+)
-- Jeito recomendado (cria um banco temporário e apaga no fim):
--   python database/run_tests.py
-- Manual, em um banco DESCARTÁVEL que já recebeu o 001_schema.sql e o seed:
--   psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/tests/002_seed_test.sql
-- Cada verificação mostra "ok: ..." ou para com "FALHOU: ...".
-- O run_tests.py roda este arquivo duas vezes: depois do seed e depois de
-- repeti-lo. Os mesmos números nas duas vezes provam que o seed não duplica nada.
-- =====================================================================

CREATE OR REPLACE FUNCTION pg_temp.verificar(descricao text, condicao boolean) RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
    IF condicao IS NOT TRUE THEN
        RAISE EXCEPTION 'FALHOU: %', descricao;
    END IF;
    RAISE NOTICE 'ok: %', descricao;
END $$;

SELECT pg_temp.verificar('20 eventos no total',
    (SELECT count(*) FROM events) = 20);
SELECT pg_temp.verificar('6 palestras, 8 workshops, 4 hackathons e 2 do tipo Outro',
    (SELECT count(*) FROM events WHERE event_type = 'Palestra')  = 6
    AND (SELECT count(*) FROM events WHERE event_type = 'Workshop')  = 8
    AND (SELECT count(*) FROM events WHERE event_type = 'Hackathon') = 4
    AND (SELECT count(*) FROM events WHERE event_type = 'Outro')     = 2);

SELECT pg_temp.verificar('nenhum evento no passado (a limpeza da US 5.1 não os apaga)',
    (SELECT count(*) FROM events WHERE int_event_date < CURRENT_DATE) = 0);
SELECT pg_temp.verificar('um evento hoje',
    (SELECT count(*) FROM events WHERE int_event_date = CURRENT_DATE) = 1);
SELECT pg_temp.verificar('um dia com 3 eventos (teste de ordenação por hora)',
    (SELECT max(c) FROM (SELECT count(*) AS c FROM events GROUP BY int_event_date) d) >= 3);

SELECT pg_temp.verificar('título longo (150+) e descrição longa (400+ caracteres)',
    (SELECT max(length(title)) FROM events) >= 150
    AND (SELECT max(length(description)) FROM events) >= 400);
SELECT pg_temp.verificar('há evento que termina em outro dia e evento sem horário de fim',
    (SELECT count(*) FROM events WHERE end_event_date > int_event_date) >= 1
    AND (SELECT count(*) FROM events WHERE end_event_date IS NULL) >= 1);
SELECT pg_temp.verificar('há eventos com e sem capacidade',
    (SELECT count(*) FROM events WHERE capacity IS NULL) >= 1
    AND (SELECT count(*) FROM events WHERE capacity IS NOT NULL) >= 1);

SELECT pg_temp.verificar('todos os eventos são ativos, manuais, sem extração e sem admin',
    (SELECT bool_and(status = 'active' AND origin = 'manual'
                     AND extraction_id IS NULL AND admin_id IS NULL) FROM events));
