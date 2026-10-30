-- =====================================================================
-- IESI-57 | US 2.1, 2.2, 2.3 | Massa de dados fictícia (20 eventos)
-- USO APENAS EM DESENVOLVIMENTO: não rodar em banco com eventos reais.
-- Pré-requisito: database/001_schema.sql já executado (PostgreSQL).
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/002_seed_eventos.sql
--
-- Usa as colunas do backend (title, event_type, registration_link...).
-- status e origin ficam no padrão do banco ('active' e 'manual').
-- As datas são relativas ao dia da execução (CURRENT_DATE + N dias), então
-- os eventos ficam sempre no futuro e a limpeza da US 5.1 não os apaga.
-- Pode rodar mais de uma vez: um evento cujo título já existe não é inserido de novo.
-- Para recomeçar do zero: TRUNCATE events RESTART IDENTITY;
--
-- Casos úteis para testar as telas:
--   * 4 tipos (6 Palestras, 8 Workshops, 4 Hackathons, 2 Outro)
--   * evento hoje, 3 eventos no mesmo dia (ordenação por hora)
--   * título com 182 caracteres e descrição com 422 (quebra de linha no layout)
--   * eventos com fim no mesmo dia, em dias seguintes (hackathons) e sem fim
--   * eventos com e sem capacidade; horários em 24h
-- =====================================================================

INSERT INTO events (title, description, date, time, location, event_type,
                    registration_link, capacity, end_date, end_time)
SELECT v.title,
       v.description,
       CURRENT_DATE + v.dias,
       v.hora::time,
       v.location,
       v.event_type,
       v.link,
       v.capacity::int,
       CURRENT_DATE + v.fim_dias::int,
       v.hora_fim::time
FROM (VALUES
    ('Palestra de Abertura do Semestre',
     'Apresentação das oportunidades acadêmicas do semestre: monitorias, iniciação científica e projetos de extensão.',
     0, '09:00', 'Auditório do CIn', 'Palestra',
     'https://example.com/inscricao/abertura-semestre', 200, 0, '11:00'),
    ('Workshop de Git e GitHub para Iniciantes',
     'Aprenda a versionar código, criar branches e abrir pull requests em projetos feitos em equipe.',
     1, '14:00', 'Laboratório de Graduação 2', 'Workshop',
     'https://example.com/inscricao/git-github', 30, 1, '17:00'),
    ('Carreiras em Ciência de Dados',
     'Bate-papo sobre áreas de atuação, formação e primeiros passos para quem quer trabalhar com dados.',
     2, '10:30', 'Auditório do CIn', 'Palestra',
     'https://example.com/inscricao/carreiras-dados', NULL, NULL, NULL),
    ('Introdução ao React',
     'Construa uma pequena aplicação com componentes, estado e rotas e conheça o ecossistema da biblioteca.',
     2, '16:00', 'Laboratório de Graduação 1', 'Workshop',
     'https://example.com/inscricao/intro-react', 25, 2, '19:00'),
    ('Segurança da Informação no Dia a Dia',
     'Boas práticas de senhas, autenticação em dois fatores e como identificar golpes de phishing.',
     2, '19:00', 'Online (Google Meet)', 'Palestra',
     'https://example.com/inscricao/seguranca-informacao', NULL, NULL, NULL),
    ('Python para Análise de Dados',
     'Oficina prática com pandas e gráficos para explorar e visualizar um conjunto de dados real.',
     5, '13:30', 'Laboratório de Graduação 3', 'Workshop',
     'https://example.com/inscricao/python-dados', 30, 5, '17:30'),
    ('Hackathon de Sustentabilidade',
     'Maratona de 24 horas para criar soluções digitais voltadas ao uso consciente de recursos no campus.',
     7, '08:00', 'Centro de Informática', 'Hackathon',
     'https://example.com/inscricao/hackathon-sustentabilidade', 80, 8, '08:00'),
    ('Inteligência Artificial Generativa na Educação',
     'Discussão sobre oportunidades, limites e cuidados no uso de IA generativa em sala de aula e nos estudos.',
     8, '15:00', 'Auditório do CIn', 'Palestra',
     'https://example.com/inscricao/ia-educacao', NULL, NULL, NULL),
    ('Modelagem de Banco de Dados com PostgreSQL',
     'Do modelo conceitual às tabelas: chaves, restrições, relacionamentos e consultas básicas em SQL.',
     9, '10:00', 'Laboratório de Graduação 2', 'Workshop',
     'https://example.com/inscricao/modelagem-postgresql', 30, 9, '13:00'),
    ('Mulheres na Tecnologia: Trajetórias e Desafios',
     'Roda de conversa com profissionais e estudantes sobre carreira, representatividade e redes de apoio.',
     12, '18:30', 'Auditório do CIn', 'Outro',
     'https://example.com/inscricao/mulheres-tecnologia', NULL, NULL, NULL),
    ('Hackathon de Saúde Digital',
     'Durante 24 horas, equipes de 3 a 5 pessoas desenvolvem protótipos de aplicativos e serviços que ajudem no acesso à informação e ao cuidado em saúde. Haverá mentoria técnica ao longo do evento, apresentação final para uma banca avaliadora e premiação para as três melhores propostas. Não é necessário ter experiência prévia em competições, e participantes de todos os cursos são bem-vindos. Traga seu notebook e carregador.',
     14, '09:00', 'Centro de Informática', 'Hackathon',
     'https://example.com/inscricao/hackathon-saude', 100, 15, '09:00'),
    ('Design de Interfaces com Figma',
     'Aprenda a criar protótipos navegáveis, componentes reutilizáveis e um guia visual simples para o seu projeto.',
     15, '14:30', 'Laboratório de Graduação 1', 'Workshop',
     'https://example.com/inscricao/figma', 25, NULL, NULL),
    ('Computação em Nuvem: Do Zero ao Deploy',
     'Visão geral de serviços de nuvem e demonstração de como publicar uma aplicação web em poucos passos.',
     18, '11:00', 'Online (Google Meet)', 'Palestra',
     'https://example.com/inscricao/nuvem-deploy', NULL, NULL, NULL),
    ('Testes Automatizados em JavaScript',
     'Escreva testes de interface e de funções com Vitest e Testing Library e entenda o que vale a pena testar.',
     21, '16:00', 'Laboratório de Graduação 3', 'Workshop',
     'https://example.com/inscricao/testes-javascript', 30, NULL, NULL),
    ('Seminário Interdisciplinar sobre Ética, Privacidade e Proteção de Dados Pessoais na Era da Inteligência Artificial: Desafios Jurídicos e Técnicos para Pesquisadores e Desenvolvedores',
     'Seminário com especialistas de computação e direito sobre LGPD, consentimento e uso responsável de dados em pesquisas.',
     24, '09:30', 'Auditório do CIn', 'Palestra',
     'https://example.com/inscricao/seminario-etica-privacidade', 150, NULL, NULL),
    ('Hackathon de Mobilidade Urbana',
     'Maratona para propor soluções que melhorem o deslocamento de estudantes e servidores até o campus.',
     28, '08:00', 'Centro de Informática', 'Hackathon',
     'https://example.com/inscricao/hackathon-mobilidade', 80, 29, '08:00'),
    ('Docker para Desenvolvedores',
     'Containers na prática: criar imagens, subir serviços com Docker Compose e padronizar o ambiente da equipe.',
     31, '14:00', 'Laboratório de Graduação 2', 'Workshop',
     'https://example.com/inscricao/docker', 30, NULL, NULL),
    ('Mercado de Trabalho em TI: Estágios e Primeiro Emprego',
     'Egressos compartilham como foi o processo seletivo, o que as empresas procuram e como montar um bom currículo.',
     35, '10:00', 'Auditório do CIn', 'Outro',
     'https://example.com/inscricao/mercado-trabalho', NULL, NULL, NULL),
    ('Introdução a Machine Learning com Scikit-learn',
     'Treine e avalie seus primeiros modelos de classificação e regressão usando Python e conjuntos de dados abertos.',
     42, '13:00', 'Laboratório de Graduação 3', 'Workshop',
     'https://example.com/inscricao/machine-learning', 30, NULL, NULL),
    ('Hackathon de Educação e Acessibilidade',
     'Equipes criam ferramentas digitais que tornem o aprendizado mais acessível para pessoas com diferentes necessidades.',
     56, '09:00', 'Centro de Informática', 'Hackathon',
     'https://example.com/inscricao/hackathon-acessibilidade', 80, 57, '09:00')
) AS v (title, description, dias, hora, location, event_type, link, capacity, fim_dias, hora_fim)
WHERE NOT EXISTS (SELECT 1 FROM events e WHERE e.title = v.title);
