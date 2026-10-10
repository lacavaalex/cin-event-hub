-- =====================================================================
-- IESI-56 | US 2.1, 2.2, 2.3 | Tabela de eventos (PostgreSQL 13+)
-- Fonte: ModeloRelacionalIESI.drawio (nomes alinhados com o backend em
-- backend/app/models: tabelas e colunas em inglês, como o SQLAlchemy usa).
-- Execução: psql -U <usuario> -d <banco> -v ON_ERROR_STOP=1 -f database/001_schema.sql
-- Rode uma vez, em banco vazio. Se o backend já criou tabelas pelo
-- create_all, apague-as antes (DROP SCHEMA public CASCADE; CREATE SCHEMA public;).
-- =====================================================================

-- ---------------------------------------------------------------------
-- users  (relacional: USUARIO) -- existe aqui só para events.admin_id (cadastra)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    email           VARCHAR(200) NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    profile_name    VARCHAR(100),
    is_admin        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- ---------------------------------------------------------------------
-- extractions  (relacional: EXTRACAO) -- existe aqui só para events.extraction_id (gera)
-- ---------------------------------------------------------------------
CREATE TABLE extractions (
    id            INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message_id    VARCHAR(255) NOT NULL,
    thread_id     VARCHAR(255),
    body_hash     VARCHAR(64)  NOT NULL,
    input_text    TEXT,
    prompt        TEXT,
    json_output   JSONB,
    status        VARCHAR(20)  NOT NULL DEFAULT 'pending',
    error_message TEXT,
    extracted_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_extractions_message_id UNIQUE (message_id)
);

-- ---------------------------------------------------------------------
-- events  (relacional: EVENTO)
-- Colunas de title..origin, created_at e updated_at batem com
-- backend/app/models/event.py. As demais são do relacional e são
-- opcionais (NULL), para o INSERT atual do backend continuar valendo.
-- ---------------------------------------------------------------------
CREATE TABLE events (
    id                INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id     INTEGER,
    admin_id          INTEGER,
    title             VARCHAR(200) NOT NULL,
    description       TEXT         NOT NULL,
    capacity          INTEGER,
    event_type        VARCHAR(50)  NOT NULL,
    date              DATE         NOT NULL,
    time              TIME         NOT NULL,
    end_date          DATE,
    end_time          TIME,
    location          VARCHAR(200) NOT NULL,
    registration_link VARCHAR(500) NOT NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'active',
    origin            VARCHAR(20)  NOT NULL DEFAULT 'manual',
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),

    -- gera: uma extração pode gerar vários eventos; extração apagada não apaga o evento.
    CONSTRAINT fk_events_extraction
        FOREIGN KEY (extraction_id) REFERENCES extractions (id) ON DELETE SET NULL,
    -- cadastra: usuário (admin) que cadastrou; apagar o usuário não apaga o evento.
    CONSTRAINT fk_events_admin
        FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE SET NULL,

    CONSTRAINT ck_events_title_preenchido       CHECK (btrim(title) <> ''),
    CONSTRAINT ck_events_description_preenchida CHECK (btrim(description) <> ''),
    CONSTRAINT ck_events_location_preenchido    CHECK (btrim(location) <> ''),
    -- mesmos tipos aceitos pelo backend (schemas/event.py: EventType)
    CONSTRAINT ck_events_event_type
        CHECK (event_type IN ('Palestra', 'Workshop', 'Hackathon', 'Outro')),
    CONSTRAINT ck_events_registration_link_http
        CHECK (registration_link ~* '^https?://\S+$'),
    CONSTRAINT ck_events_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT ck_events_capacity CHECK (capacity IS NULL OR capacity > 0),
    -- fim do evento: ou vem completo, ou não vem; e não pode ser antes do início
    CONSTRAINT ck_events_fim_completo
        CHECK ((end_date IS NULL) = (end_time IS NULL)),
    CONSTRAINT ck_events_fim_apos_inicio
        CHECK (end_date IS NULL OR (end_date, end_time) >= (date, time))
);
-- A regra "data não pode estar no passado" (US 2.1) fica no backend
-- (PastEventDateError): um CHECK com CURRENT_DATE quebraria restore de backup
-- e a limpeza de eventos expirados (E5).
