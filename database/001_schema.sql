CREATE TABLE usuario ( 
	id_usuario 		INTEGER 		GENERATED ALWAYS AS IDENTITY, 
	nome 			VARCHAR(90) 	NOT NULL, 
	email 			VARCHAR(200) 	NOT NULL,
	senha_hash 		VARCHAR(100)	NOT NULL,
	nome_perfil 	VARCHAR(50)		NOT NULL,
	is_admin 		BOOLEAN 		NOT NULL DEFAULT FALSE,
	dt_cadastro		DATE			NOT NULL DEFAULT CURRENT_DATE,

	CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
	CONSTRAINT uk_usuario_email UNIQUE (email),

	CONSTRAINT ck_usuario_nome_preenchido       CHECK (btrim(nome) <> ''),
	CONSTRAINT ck_usuario_email_preenchido       CHECK (btrim(email) <> ''),
	CONSTRAINT ck_usuario_senha_hash_preenchida  CHECK (btrim(senha_hash) <> ''),
	CONSTRAINT ck_usuario_nome_perfil_preenchido CHECK (btrim(nome_perfil) <> '')
);


CREATE TABLE extracao (
	id_extracao		INTEGER			GENERATED ALWAYS AS IDENTITY,
	message_id		VARCHAR(255)	NOT NULL,
	thread_id		VARCHAR(255)	NOT NULL,
	body_hash 		VARCHAR(64)		NOT NULL,
	input_text		TEXT,
	prompt			TEXT			NOT NULL,
	json_output		JSONB,
	status			VARCHAR(20)		NOT NULL DEFAULT 'pending' 
		CHECK (status IN ('pending', 'success', 'failed')),
	error_message 	TEXT,
    extracted_at  	TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT pk_extracao PRIMARY KEY (id_extracao),
	CONSTRAINT ck_extracao_message_id_preenchido CHECK (btrim(message_id) <> ''),
	CONSTRAINT ck_extracao_thread_id_preenchido  CHECK (btrim(thread_id) <> ''),
	CONSTRAINT ck_extracao_body_hash_valido      CHECK (length(body_hash) = 64),
	CONSTRAINT ck_extracao_prompt_preenchido     CHECK (btrim(prompt) <> '')
);

CREATE UNIQUE INDEX uk_sucesso_de_extracao
ON extracao(message_id, thread_id) WHERE status = 'success';


CREATE TABLE events (
	id_event         INTEGER      GENERATED ALWAYS AS IDENTITY,
    extraction_id     INTEGER,
    admin_id          INTEGER,
    title             VARCHAR(200) NOT NULL,
    description       TEXT         NOT NULL,
    capacity          INTEGER,
    event_type        VARCHAR(50)  NOT NULL,
    int_event_date    DATE         NOT NULL,
    int_event_time    TIME         NOT NULL,
    end_event_date    DATE,
    end_event_time    TIME,
    event_location    VARCHAR(200) NOT NULL,
    registration_link VARCHAR(500) NOT NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'active',
    origin            VARCHAR(20)  NOT NULL DEFAULT 'manual',
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT pk_events PRIMARY KEY (id_event),
	CONSTRAINT fk_events_extracao 
		FOREIGN KEY (extraction_id) REFERENCES extracao(id_extracao) ON DELETE SET NULL,
	CONSTRAINT fk_events_usuario
		FOREIGN KEY (admin_id) REFERENCES usuario(id_usuario) ON DELETE SET NULL,
		
	CONSTRAINT ck_events_title_preenchido       CHECK (btrim(title) <> ''),
    CONSTRAINT ck_events_description_preenchida CHECK (btrim(description) <> ''),
    CONSTRAINT ck_events_location_preenchido    CHECK (btrim(event_location) <> ''),

	CONSTRAINT ck_events_event_type
        CHECK (event_type IN ('Palestra', 'Workshop', 'Hackathon', 'Outro')),
    CONSTRAINT ck_events_registration_link_http
        CHECK (registration_link ~* '^https?://\S+$'),
    CONSTRAINT ck_events_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT ck_events_capacity CHECK (capacity IS NULL OR capacity > 0),
    CONSTRAINT ck_events_fim_completo
        CHECK ((end_event_date IS NULL) = (end_event_time IS NULL)),
    CONSTRAINT ck_events_fim_apos_inicio
        CHECK (end_event_date IS NULL OR (end_event_date, end_event_time) >= (int_event_date, int_event_time)),
	CONSTRAINT ck_events_criador_unico
    CHECK (NOT (extraction_id IS NOT NULL AND admin_id IS NOT NULL))
);

CREATE INDEX data_evento
ON events(int_event_date);

CREATE INDEX tipo_evento
ON events(event_type);

CREATE INDEX titulo_evento
ON events(title);

CREATE TABLE favorito (
	id_usuario	  	INTEGER		NOT NULL,
	id_events      	INTEGER		NOT NULL,

	CONSTRAINT pk_favorito PRIMARY KEY (id_usuario, id_events),
	CONSTRAINT fk_favorito_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
	CONSTRAINT fk_favorito_evento FOREIGN KEY (id_events) REFERENCES events(id_event) ON DELETE CASCADE
);

CREATE TABLE email_associado (
	id_extracao		INTEGER		NOT NULL,
	id_evento		INTEGER		NOT NULL,

	CONSTRAINT pk_email_associado PRIMARY KEY (id_extracao, id_evento),
	CONSTRAINT fk_email_associado_extracao FOREIGN KEY (id_extracao) REFERENCES extracao(id_extracao) ON DELETE CASCADE,
	CONSTRAINT fk_email_associado_events FOREIGN KEY (id_evento) REFERENCES events(id_event) ON DELETE CASCADE
);
