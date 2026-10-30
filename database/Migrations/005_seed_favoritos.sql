-- =====================================================================
-- Massa de dados fictícia (8 favoritos)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com favoritos reais.
-- Pré-requisitos (PostgreSQL), nesta ordem:
--   database/001_schema.sql, 002_seed_eventos.sql e 003_seed_usuarios.sql
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/005_seed_favoritos.sql
--
-- Os vínculos são resolvidos por e-mail do usuário e título do evento, porque os
-- ids são gerados automaticamente (GENERATED ALWAYS AS IDENTITY).
-- Se o usuário ou o evento não existir, a linha é ignorada em silêncio: confira
-- com SELECT count(*) FROM favorito; (esperado: 8).
-- Pode rodar mais de uma vez: um favorito que já existe não é inserido de novo.
-- Para recomeçar do zero: TRUNCATE favorito;
--
-- Casos úteis para testar as telas:
--   * usuário com 3 favoritos, usuários com 2 e com 1
--   * evento favoritado por mais de um usuário (Hackathon de Saúde Digital)
--   * favorito em evento que acontece hoje (Palestra de Abertura do Semestre)
--   * administrador também favoritando eventos
-- =====================================================================

INSERT INTO favorito (id_usuario, id_events)
SELECT u.id_usuario, e.id_event
FROM (VALUES
    ('marina.souza@example.com',    'Workshop de Git e GitHub para Iniciantes'),
    ('marina.souza@example.com',    'Python para Análise de Dados'),
    ('marina.souza@example.com',    'Hackathon de Saúde Digital'),
    ('pedro.costa@example.com',     'Hackathon de Saúde Digital'),
    ('pedro.costa@example.com',     'Modelagem de Banco de Dados com PostgreSQL'),
    ('julia.fernandes@example.com', 'Palestra de Abertura do Semestre'),
    ('julia.fernandes@example.com', 'Mulheres na Tecnologia: Trajetórias e Desafios'),
    ('ana.lima@example.com',        'Hackathon de Sustentabilidade')
) AS v (email, titulo)
JOIN usuario u ON u.email = v.email
JOIN events  e ON e.title = v.titulo
WHERE NOT EXISTS (SELECT 1 FROM favorito f
                  WHERE f.id_usuario = u.id_usuario AND f.id_events = e.id_event);
