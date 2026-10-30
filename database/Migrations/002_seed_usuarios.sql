-- =====================================================================
-- Massa de dados fictícia (5 usuários)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com usuários reais.
-- Pré-requisito: database/001_schema.sql já executado (PostgreSQL).
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/003_seed_usuarios.sql
--
-- Os hashes de senha são FICTÍCIOS: não correspondem a nenhuma senha real,
-- então ninguém consegue fazer login com estes usuários. Para testar login,
-- gere hashes bcrypt de verdade.
-- Os e-mails usam o domínio example.com para não coincidir com contas reais.
-- dt_cadastro é relativa ao dia da execução (CURRENT_DATE - N dias).
-- Pode rodar mais de uma vez: um usuário cujo e-mail já existe não é inserido de novo.
-- Para recomeçar do zero: DELETE FROM usuario WHERE email LIKE '%@example.com';
--   (os favoritos somem em cascata; eventos criados por eles ficam com admin_id NULL)
--
-- Casos úteis para testar as telas:
--   * 2 administradores e 3 usuários comuns
--   * nome com acento (Júlia) e nome composto grande
--   * datas de cadastro espalhadas nos últimos 3 meses
-- =====================================================================

INSERT INTO usuario (nome, email, senha_hash, nome_perfil, is_admin, dt_cadastro)
SELECT v.nome,
       v.email,
       v.senha_hash,
       v.nome_perfil,
       v.is_admin::boolean,
       CURRENT_DATE - v.dias_atras
FROM (VALUES
    ('Ana Beatriz Lima',
     'ana.lima@example.com',
     '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY01',
     'anabl', TRUE, 80),
    ('Carlos Eduardo Silva',
     'carlos.silva@example.com',
     '$2b$12$bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ02',
     'cadu', TRUE, 78),
    ('Marina Souza',
     'marina.souza@example.com',
     '$2b$12$cdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZA03',
     'marisouza', FALSE, 60),
    ('Pedro Henrique Costa',
     'pedro.costa@example.com',
     '$2b$12$defghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZAB04',
     'pedrohc', FALSE, 45),
    ('Júlia Fernandes',
     'julia.fernandes@example.com',
     '$2b$12$efghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZABC05',
     'juf', FALSE, 27)
) AS v (nome, email, senha_hash, nome_perfil, is_admin, dias_atras)
WHERE NOT EXISTS (SELECT 1 FROM usuario u WHERE u.email = v.email);
