<div align="center">

# CIn Event Hub

### Um ponto de encontro para os eventos e oportunidades acadêmicas do Centro de Informática da UFPE.

**Da caixa de entrada institucional à descoberta de eventos: captura automatizada, extração inteligente, validação e publicação em uma única plataforma.**

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL 16" />
  <img src="https://img.shields.io/badge/React-19-149ECA?style=flat-square&logo=react&logoColor=white" alt="React 19" />
  <img src="https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite 8" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker Compose" />
  <img src="https://img.shields.io/badge/Nginx-1.27-009639?style=flat-square&logo=nginx&logoColor=white" alt="Nginx" />
  <img src="https://img.shields.io/badge/OpenRouter-LLM-6B4EFF?style=flat-square&logo=openai&logoColor=white" alt="OpenRouter" />
  <img src="https://img.shields.io/badge/IESI-2026.2-8A2BE2?style=flat-square" alt="IESI 2026.2" />
</p>

[Visão geral](#visão-geral) · [Funcionalidades](#funcionalidades) · [Tecnologias](#tecnologias) · [Arquitetura](#arquitetura) · [Banco de dados](#modelo-de-dados) · [Início rápido](#início-rápido) · [Equipe](#equipe-e-contribuições)

**Projeto acadêmico desenvolvido no contexto da disciplina Integração e Evolução de Sistemas de Informação (IESI) — Centro de Informática, Universidade Federal de Pernambuco (CIn-UFPE).**

</div>

---

## Sumário

- [Visão geral](#visão-geral)
- [O problema](#o-problema)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Fluxo de extração inteligente](#fluxo-de-extração-inteligente)
- [Modelo de dados](#modelo-de-dados)
  - [Diagrama EER](#diagrama-eer)
  - [Modelo relacional](#modelo-relacional)
- [Jornadas de uso](#jornadas-de-uso)
- [API](#api)
- [Início rápido](#início-rápido)
- [Testes e qualidade](#testes-e-qualidade)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Documentação](#documentação)
- [Equipe e contribuições](#equipe-e-contribuições)
- [Limitações conhecidas](#limitações-conhecidas)

---

## Visão geral

O **CIn Event Hub** é uma plataforma web que centraliza a divulgação de eventos acadêmicos do Centro de Informática da UFPE. Ele combina duas frentes:

1. **Descoberta:** estudantes e visitantes consultam eventos em uma interface web, com listagem cronológica, busca, filtros e página de detalhes.
2. **Ingestão automatizada:** o backend lê uma caixa institucional do Gmail, interpreta os comunicados, recorre a um modelo de linguagem quando a extração convencional não basta e valida os dados antes de publicá-los.

Um painel administrativo permite autenticar curadores, gerenciar eventos e acompanhar a rotina de extração.

## O problema

Os anúncios de oportunidades acadêmicas ficam espalhados entre e-mails e canais diferentes, o que dificulta saber o que está acontecendo e manter uma listagem organizada. O CIn Event Hub propõe um fluxo único:

- **Capturar** comunicados da caixa institucional;
- **Interpretar** mensagens estruturadas e textos livres;
- **Validar** os dados e descartar registros incompletos ou inválidos;
- **Evitar duplicidades** quando um novo e-mail é apenas lembrete de um evento já cadastrado;
- **Disponibilizar** os eventos em uma interface pública e em um painel de gerenciamento.

## Funcionalidades

<table>
  <thead>
    <tr>
      <th>Área</th>
      <th>Funcionalidades</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>🌐 Consulta pública</strong></td>
      <td>Listagem cronológica paginada de eventos ativos e não expirados; busca por título ou descrição; filtro por tipo (<code>Palestra</code>, <code>Workshop</code>, <code>Hackathon</code>, <code>Outro</code>); destaque dos eventos da semana; página de detalhes com link de inscrição e opção de adicionar à agenda.</td>
    </tr>
    <tr>
      <td><strong>🛡️ Painel administrativo</strong></td>
      <td>Login de administradores com JWT; listagem com eventos expirados sinalizados; criação, edição e exclusão de eventos; painel de status e alertas da extração. A extração e a limpeza também podem ser disparadas manualmente pela API.</td>
    </tr>
    <tr>
      <td><strong>📨 Extração de e-mails</strong></td>
      <td>Leitura da caixa institucional via Gmail API (OAuth 2.0, somente leitura); parser heurístico; fallback para modelo de linguagem via OpenRouter; validação, desduplicação e registro do resultado de cada mensagem.</td>
    </tr>
    <tr>
      <td><strong>⏱️ Processos automáticos</strong></td>
      <td>Varredura periódica da caixa de e-mails e limpeza diária de eventos expirados, com fuso de referência <code>America/Recife</code>.</td>
    </tr>
    <tr>
      <td><strong>🎨 Experiência visual</strong></td>
      <td>Interface React responsiva, com tema claro e escuro.</td>
    </tr>
  </tbody>
</table>

## Tecnologias

| Camada | Tecnologias | Uso |
|---|---|---|
| **Frontend** | React 19, React Router 7, Vite 8, JavaScript, CSS | SPA, navegação, busca, filtros e consumo da API |
| **Backend** | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2 | API REST, validação, regras de negócio e persistência |
| **Banco de dados** | PostgreSQL 16, SQL, psycopg 3 | Integridade referencial, restrições e índices |
| **Captura de e-mails** | Gmail API, Google OAuth 2.0 | Leitura das mensagens da caixa institucional |
| **Inteligência artificial** | OpenRouter (API compatível com OpenAI) | Fallback de extração quando o parser não interpreta a mensagem |
| **Agendamento** | APScheduler | Extração periódica e limpeza de eventos expirados |
| **Autenticação** | JWT (python-jose), Passlib, bcrypt | Login de administradores e proteção das rotas restritas |
| **Infraestrutura** | Docker, Nginx | Imagens do backend e do frontend |
| **Qualidade** | Pytest, HTTPX, pytest-mock, ESLint, Node Test Runner | Testes automatizados e análise estática |

## Arquitetura

A solução utiliza uma arquitetura cliente-servidor em **três camadas lógicas**: apresentação (SPA React), aplicação (API FastAPI) e dados (SQLAlchemy/PostgreSQL). O backend é um **monólito modular**: API REST, regras de negócio, extração de e-mails e tarefas agendadas pertencem à mesma aplicação FastAPI, sem divisão em microserviços. As integrações externas são acessadas por esse backend.

```mermaid
flowchart LR
    subgraph CLIENTES[Clientes]
        WEB["Navegador\nReact + Vite"]
        ADMIN["Curador\nPainel administrativo"]
    end

    subgraph BACKEND[Servidor de aplicação · FastAPI]
        API["API REST\nRouters + Pydantic"]
        SERVICES["Serviços\nRegras de negócio"]
        REPOS["Repositories\nSQLAlchemy"]
        JOBS["APScheduler\nExtração + limpeza"]
    end

    subgraph DADOS[Persistência]
        DB[("PostgreSQL")]
    end

    subgraph EXTERNOS[Integrações externas]
        GMAIL["Gmail API\nOAuth 2.0"]
        LLM["OpenRouter\nModelo de linguagem"]
    end

    WEB -->|"HTTPS / JSON"| API
    ADMIN -->|"HTTPS + JWT"| API
    API --> SERVICES
    SERVICES --> REPOS
    REPOS --> DB
    JOBS --> GMAIL
    GMAIL --> JOBS
    JOBS --> SERVICES
    SERVICES --> LLM
    LLM --> SERVICES

    classDef client fill:#E8F3FF,stroke:#2673B8,color:#15324B,stroke-width:1.5px;
    classDef app fill:#EAF7F2,stroke:#168567,color:#123D32,stroke-width:1.5px;
    classDef storage fill:#FFF4DF,stroke:#C78313,color:#553A0A,stroke-width:1.5px;
    classDef external fill:#F3ECFF,stroke:#7952B3,color:#38245A,stroke-width:1.5px;
    class WEB,ADMIN client;
    class API,SERVICES,REPOS,JOBS app;
    class DB storage;
    class GMAIL,LLM external;
```

### Responsabilidades por camada

| Camada | Responsabilidade |
|---|---|
| **Frontend** | Apresentar eventos, controlar navegação e estados da interface e consumir os endpoints REST. |
| **API** | Receber requisições, validar payloads com Pydantic, aplicar autenticação e delegar operações aos serviços. |
| **Services** | Concentrar as regras de negócio: eventos, autenticação, extração, validação, favoritos e limpeza. |
| **Repositories** | Encapsular consultas e operações de persistência com SQLAlchemy. |
| **PostgreSQL** | Garantir persistência, chaves estrangeiras, restrições `CHECK`, unicidade e índices. |
| **Jobs** | Executar rotinas periódicas sem depender de uma requisição do navegador. |

### Estilo arquitetural e organização do projeto

| Conceito | Como é aplicado no CIn Event Hub |
|---|---|
| **Arquitetura em três camadas** | **Apresentação:** React SPA no navegador. **Aplicação:** FastAPI, routers, services e agendadores. **Dados:** repositories, modelos SQLAlchemy e PostgreSQL. |
| **Monólito modular** | O backend é implantado como uma aplicação FastAPI. Os módulos de autenticação, eventos, favoritos e extração são separados por responsabilidade, mas não são serviços independentes. |
| **Arquitetura em camadas no backend** | As rotas recebem requisições e validam entradas; os services concentram regras de negócio; repositories encapsulam o acesso aos dados; models representam o mapeamento ORM. |
| **Separação inspirada em MVC** | Os routers exercem o papel de controllers, os models representam os dados e a interface React concentra as views. Não é um MVC clássico renderizado no servidor: frontend e backend são aplicações separadas que se comunicam por REST/JSON. |
| **Frontend SPA** | React e React Router controlam páginas e navegação no cliente; o backend fornece os dados por endpoints REST. |

## Fluxo de extração inteligente

O motor de extração combina regras determinísticas com um modelo de linguagem. A IA é usada apenas como **fallback**, quando o parser não obtém os dados necessários, e nunca substitui a validação.

```mermaid
flowchart TD
    START([Execução manual ou agendada]) --> GMAIL[Consultar Gmail API]
    GMAIL --> NEW{Mensagem já registrada?}
    NEW -- Sim --> DUP[Contabilizar duplicata]
    NEW -- Não --> PARSER[Parser heurístico]
    PARSER --> PARSE_OK{Campos suficientes?}
    PARSE_OK -- Sim --> VALIDATE[Validação autônoma]
    PARSE_OK -- Não --> AI[OpenRouter · modelo configurado]
    AI --> AI_EVENT{É um evento com dados suficientes?}
    AI_EVENT -- Não --> LOG_IGNORE[Registrar ignorado ou extração incompleta]
    AI_EVENT -- Sim --> VALIDATE
    VALIDATE --> VALID{Dados íntegros e data válida?}
    VALID -- Não --> LOG_INVALID[Registrar descarte / alerta]
    VALID -- Sim --> SAME{Evento ativo semelhante\ncom a mesma data?}
    SAME -- Sim --> LOG_DUP[Registrar lembrete duplicado]
    SAME -- Não --> SAVE[Persistir evento]
    SAVE --> LOG_OK[Registrar extração processada]
    DUP --> END([Fim do ciclo])
    LOG_IGNORE --> END
    LOG_INVALID --> END
    LOG_DUP --> END
    LOG_OK --> END

    classDef input fill:#E8F3FF,stroke:#2673B8,color:#15324B;
    classDef decision fill:#FFF4DF,stroke:#C78313,color:#553A0A;
    classDef ai fill:#F3ECFF,stroke:#7952B3,color:#38245A;
    classDef success fill:#EAF7F2,stroke:#168567,color:#123D32;
    classDef log fill:#F3F4F6,stroke:#6B7280,color:#1F2937;
    class GMAIL,PARSER input;
    class NEW,PARSE_OK,AI_EVENT,VALID,SAME decision;
    class AI ai;
    class SAVE,LOG_OK success;
    class DUP,LOG_IGNORE,LOG_INVALID,LOG_DUP log;
```

1. **Captura:** o cliente do Gmail lê as mensagens que atendem à consulta configurada (`GMAIL_QUERY`), com escopo `gmail.readonly`.
2. **Idempotência:** mensagens cujo `gmail_message_id` já consta no histórico não são reprocessadas.
3. **Parser:** regras heurísticas extraem título, data, hora, local, tipo, descrição e link.
4. **Fallback de IA:** quando faltam dados, o cliente de IA consulta o modelo configurado por meio do OpenRouter.
5. **Validação:** verifica estrutura e requisitos mínimos, incluindo uma data de evento válida.
6. **Desduplicação:** compara o título, sem diferenciar caixa, acentos, pontuação ou marcadores como "Lembrete:", com os eventos ativos da mesma data. Títulos iguais ou com similaridade de pelo menos 0,85 são tratados como lembrete e não geram novo evento.
7. **Persistência e histórico:** eventos aceitos são gravados; toda mensagem processada recebe um status na tabela `extracao`: `processado`, `processado_ia`, `ignorado`, `nao_processado`, `extracao_incompleta`, `ignorado_duplicata` ou `erro`.

**Agendamento.** A varredura é iniciada pelo ciclo de vida do FastAPI quando `EXTRACTION_ENABLED` está ativo e as credenciais do Gmail estão disponíveis; o intervalo padrão é de 720 minutos (12 horas). A limpeza de eventos expirados roda diariamente às 03:00 em `America/Recife`, salvo configuração diferente.

**Privacidade.** O remetente é reduzido ao domínio, dados pessoais em campos de log são mascarados e o corpo integral do e-mail não é persistido. Detalhes em [`docs/reports/technical/lgpd-minimizacao-dados.md`](docs/reports/technical/lgpd-minimizacao-dados.md).

## Modelo de dados

Os diagramas representam o schema vigente em [`database/001_schema.sql`](database/001_schema.sql). O administrador **não** tem tabela própria: é um registro de `usuario` com `is_admin = TRUE`.

### Diagrama EER

O diagrama conceitual usa retângulos para entidades, elipses para atributos principais e losangos para relacionamentos. Ele destaca identificadores e os atributos que diferenciam cada entidade; todas as colunas aparecem no modelo relacional logo abaixo.

```mermaid
flowchart TB
    U["USUARIO"]:::entidade
    E["EVENTO"]:::entidade
    X["EXTRACAO"]:::entidade

    CAD{"CADASTRA"}:::relacao
    FAV{"FAVORITA"}:::relacao
    VINC{"VINCULA"}:::relacao

    U_ID(["id_usuario · PK"]):::atributo
    U_EMAIL(["email · UNIQUE"]):::atributo
    U_ADMIN(["is_admin"]):::atributo

    E_ID(["id_event · PK"]):::atributo
    E_ADMIN(["admin_id · FK opcional"]):::atributo
    E_TITLE(["title"]):::atributo
    E_DATE(["int_event_date"]):::atributo

    X_ID(["id · PK"]):::atributo
    X_MSG(["gmail_message_id · UNIQUE"]):::atributo
    X_STATUS(["status"]):::atributo
    X_EVENT(["event_id · FK opcional"]):::atributo

    U --- U_ID
    U --- U_EMAIL
    U --- U_ADMIN

    E --- E_ID
    E --- E_ADMIN
    E --- E_TITLE
    E --- E_DATE

    X --- X_ID
    X --- X_MSG
    X --- X_STATUS
    X --- X_EVENT

    U ---|"0..N"| CAD
    CAD ---|"0..1"| E

    U ---|"N"| FAV
    FAV ---|"M"| E

    E ---|"0..N"| VINC
    VINC ---|"0..1"| X

    classDef entidade fill:#DCEBFF,stroke:#2B6CB0,color:#17365D,stroke-width:2px;
    classDef atributo fill:#F8FAFC,stroke:#94A3B8,color:#263238,stroke-width:1px;
    classDef relacao fill:#FFF2CC,stroke:#C28A16,color:#604500,stroke-width:2px;
```

- **USUARIO — CADASTRA — EVENTO:** um usuário pode cadastrar zero ou muitos eventos; cada evento tem zero ou um usuário responsável (`events.admin_id` é opcional).
- **USUARIO — FAVORITA — EVENTO:** relacionamento muitos-para-muitos, implementado pela tabela associativa `favorito`.
- **EVENTO — VINCULA — EXTRACAO:** um evento pode ser referenciado por zero ou muitos registros de extração; cada registro aponta para zero ou um evento (`extracao.event_id` é opcional). `EXTRACAO` é o histórico de processamento das mensagens, não uma entidade de e-mail.

### Modelo relacional

As quatro tabelas do banco, com colunas, tipos e restrições de chave primária (PK), estrangeira (FK) e unicidade (UK).

```mermaid
erDiagram
    direction LR

    usuario {
        INTEGER id_usuario PK
        VARCHAR nome "VARCHAR(90)"
        VARCHAR email UK "VARCHAR(200)"
        VARCHAR senha_hash "VARCHAR(100)"
        VARCHAR nome_perfil "VARCHAR(50)"
        BOOLEAN is_admin
        DATE dt_cadastro
    }

    events {
        INTEGER id_event PK
        INTEGER admin_id FK "nullable"
        VARCHAR title "VARCHAR(200)"
        TEXT description
        INTEGER capacity "nullable"
        VARCHAR event_type "VARCHAR(50)"
        DATE int_event_date
        TIME int_event_time
        DATE end_event_date "nullable"
        TIME end_event_time "nullable"
        VARCHAR event_location "VARCHAR(200)"
        VARCHAR registration_link "VARCHAR(500)"
        VARCHAR status "VARCHAR(20)"
        VARCHAR origin "VARCHAR(20)"
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    extracao {
        INTEGER id PK
        VARCHAR gmail_message_id UK "VARCHAR(64)"
        VARCHAR source_email "VARCHAR(255)"
        VARCHAR status "VARCHAR(20)"
        JSON extracted_data "nullable"
        VARCHAR error_message "nullable · VARCHAR(500)"
        INTEGER event_id FK "nullable"
        TIMESTAMPTZ created_at
    }

    favorito {
        INTEGER id_usuario PK, FK
        INTEGER id_events PK, FK
    }

    usuario o|--o{ events : "admin_id"
    events o|--o{ extracao : "event_id"
    usuario ||--o{ favorito : "id_usuario"
    events ||--o{ favorito : "id_events"
```

### Integridade e índices

| Regra no banco | Implementação |
|---|---|
| Identidade de usuário | `id_usuario` como chave primária e `email` único. |
| Tipos de evento | `event_type` restrito a `Palestra`, `Workshop`, `Hackathon` e `Outro`. |
| Link de inscrição | URL `http(s)` obrigatória em eventos manuais; eventos extraídos podem não ter link. |
| Capacidade | Quando informada, maior que zero. |
| Período do evento | Data e hora de término informadas em conjunto e nunca anteriores ao início. |
| Responsável pelo evento | `events.admin_id` usa `ON DELETE SET NULL`. |
| Histórico de extração | `gmail_message_id` único; `event_id` usa `ON DELETE SET NULL` e só é preenchido em `processado` e `processado_ia`. |
| Favoritos | Chave primária composta e exclusão em cascata para usuário e evento. |
| Consultas | Índice parcial por data, hora e id para eventos ativos; índices por tipo e por título. |

> [!NOTE]
> Os diagramas e os documentos de banco em [`docs/architecture/database/`](docs/architecture/database/) registram etapas anteriores da modelagem e podem divergir do schema atual. Em caso de dúvida, vale o SQL versionado.

## Jornadas de uso

### Visitante: descobrir um evento

```mermaid
flowchart LR
    A([Acessar a plataforma]) --> B[Home · lista de eventos]
    B --> C[Buscar por palavra-chave]
    B --> D[Filtrar por tipo]
    B --> E[Ver destaque da semana]
    C --> F[Selecionar evento]
    D --> F
    E --> F
    F --> G[Página de detalhes]
    G --> H[Consultar data, hora e local]
    G --> I[Abrir link de inscrição]
    G --> J[Adicionar à agenda]

    classDef start fill:#E8F3FF,stroke:#2673B8,color:#15324B;
    classDef action fill:#EAF7F2,stroke:#168567,color:#123D32;
    classDef terminal fill:#FFF4DF,stroke:#C78313,color:#553A0A;
    class A start;
    class B,C,D,E,F,G,H action;
    class I,J terminal;
```

### Curador: gerenciar a plataforma

```mermaid
sequenceDiagram
    actor Curador
    participant SPA as Frontend React
    participant API as FastAPI
    participant DB as PostgreSQL

    Curador->>SPA: Acessa /login e envia credenciais
    SPA->>API: POST /auth/login
    API->>DB: Localiza usuario e verifica hash
    DB-->>API: Registro com is_admin = TRUE
    API-->>SPA: JWT
    SPA->>SPA: Guarda token e libera /admin
    Curador->>SPA: Consulta eventos do painel
    SPA->>API: GET /events/admin + Bearer JWT
    API->>DB: Consulta eventos
    DB-->>API: Eventos
    API-->>SPA: Lista administrativa
    Curador->>SPA: Cria, edita ou exclui evento
    SPA->>API: POST /events · PUT /events/{id} · DELETE /events/{id}
    API->>DB: Valida regras e persiste alteração
    DB-->>API: Resultado
    API-->>SPA: Resposta HTTP
```

## API

Com o backend em execução, a documentação interativa fica em `http://localhost:8000/docs` (Swagger UI) e `http://localhost:8000/openapi.json`.

| Método | Endpoint | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/` | Público | Verificação de disponibilidade da API. |
| `POST` | `/auth/login` | Público | Autentica um administrador e retorna o JWT. |
| `GET` | `/events` | Público | Lista eventos ativos e não expirados, paginados. |
| `GET` | `/events/{event_id}` | Público | Detalhes de um evento. |
| `GET` | `/events/favorites` | `X-User-Id` | Lista os favoritos do identificador informado. |
| `POST` | `/events/{event_id}/favorite` | `X-User-Id` | Registra um favorito. |
| `DELETE` | `/events/{event_id}/favorite` | `X-User-Id` | Remove um favorito. |
| `POST` | `/events` | JWT de admin | Cria um evento manual. |
| `GET` | `/events/admin` | JWT de admin | Lista todos os eventos, com `is_expired` indicando os vencidos. |
| `PUT` | `/events/{event_id}` | JWT de admin | Atualiza um evento. |
| `DELETE` | `/events/{event_id}` | JWT de admin | Exclui um evento. |
| `POST` | `/events/cleanup` | JWT de admin | Executa a limpeza de eventos expirados. |
| `POST` | `/extraction/run` | JWT de admin | Dispara um ciclo de extração. |
| `GET` | `/extraction/status` | JWT de admin | Resumo operacional da extração. |
| `GET` | `/extraction/alerts` | JWT de admin | Registros que exigem atenção. |

**Paginação.** `GET /events` aceita `page` (padrão `1`) e `page_size` (padrão `20`, máximo `100`) e responde com `items`, `page` e `total_pages`. A ordenação por data, hora e identificador mantém a ordem estável entre páginas. Contrato completo em [`docs/reports/technical/paginacao-eventos.md`](docs/reports/technical/paginacao-eventos.md).

> [!WARNING]
> Os endpoints de favoritos identificam o usuário pelo cabeçalho `X-User-Id`, sem autenticação equivalente ao JWT administrativo, e o frontend ainda não oferece uma jornada completa de favoritos. Trate o recurso como em evolução, não como autenticação de usuário final pronta para produção.

## Início rápido

### Requisitos

| Ferramenta | Versão | Uso |
|---|---:|---|
| Python | 3.12 | Backend FastAPI. |
| Node.js | 20.19+ ou 22.12+ | Frontend (exigência do Vite 8). |
| PostgreSQL | 16 | Banco de dados. |
| Docker | Opcional | Subir o PostgreSQL local. |

### 1. Clonar o repositório

```bash
git clone https://github.com/lacavaalex/cin-event-hub.git
cd cin-event-hub
```

### 2. Subir o PostgreSQL

Uma opção é executar o PostgreSQL em um container:

```bash
docker run --name cin-event-hub-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=dev_local_change_me \
  -e POSTGRES_DB=cin_event_hub \
  -p 5432:5432 \
  -d postgres:16-alpine
```

Aplique o schema a partir da raiz do projeto:

```bash
psql -h localhost -U postgres -d cin_event_hub \
  -v ON_ERROR_STOP=1 -f database/001_schema.sql
```

Opcionalmente, carregue os eventos de demonstração:

```bash
psql -h localhost -U postgres -d cin_event_hub \
  -v ON_ERROR_STOP=1 -f database/002_seed_eventos.sql
```

### 3. Configurar e iniciar o backend

```bash
cd backend

# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
# cp .env.example .env
```

Edite `backend/.env` e configure, no mínimo:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:dev_local_change_me@localhost:5432/cin_event_hub
SECRET_KEY=COLOQUE_AQUI_UMA_CHAVE_ALEATORIA_COM_PELO_MENOS_32_CARACTERES
ADMIN_EMAIL=admin@exemplo.com
ADMIN_PASSWORD=defina_uma_senha_local
```

`ADMIN_EMAIL` e `ADMIN_PASSWORD` definem o primeiro administrador, criado automaticamente na inicialização. Uma chave para `SECRET_KEY` pode ser gerada com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Crie o ambiente virtual, instale as dependências e inicie a API:

```bash
# Windows PowerShell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# python3.12 -m venv .venv
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000`.

### 4. Configurar e iniciar o frontend

Em outro terminal, a partir da raiz do repositório:

```bash
cd frontend

# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
# cp .env.example .env

npm ci
npm run dev
```

Interface disponível em `http://localhost:5173`. O painel administrativo fica em `/login`, com o e-mail e a senha definidos em `ADMIN_EMAIL` e `ADMIN_PASSWORD`.

### 5. Integrações opcionais

A aplicação inicia sem a IA e sem a extração automática. Essas funções dependem de credenciais próprias:

- **Gmail:** crie as credenciais OAuth 2.0 (aplicativo para computador) no Google Cloud, aponte `GMAIL_CREDENTIALS_FILE` e `GMAIL_TOKEN_FILE` para os arquivos no servidor e ajuste `GMAIL_QUERY`. O token é gerado na primeira autorização.
- **OpenRouter:** defina `OPENROUTER_API_KEY` e `OPENROUTER_BASE_URL`. O modelo é escolhido em `GEMINI_MODEL`; o nome é histórico e aceita qualquer identificador de modelo do OpenRouter.
- **Agendamento:** `EXTRACTION_ENABLED` e `EXTRACTION_INTERVAL_MINUTES` controlam a extração; `CLEANUP_ENABLED`, `CLEANUP_CRON_HOUR` e `CLEANUP_CRON_MINUTE` controlam a limpeza.

O passo a passo está no [guia de integração com o OpenRouter e execução local](docs/guides/integracao-openrouter-execucao-local.pdf).

> [!CAUTION]
> Nunca versione `backend/.env`, chaves de API, credenciais OAuth, tokens do Gmail ou senhas reais. Use segredos diferentes em cada ambiente.

## Testes e qualidade

**Backend** — a partir de `backend/`:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Os testes criam e removem um banco temporário (`iesi_test_backend`) no servidor PostgreSQL indicado por `DATABASE_ADMIN_URL`. O padrão é `postgresql://postgres:dev@localhost:5432/postgres`; para o container da seção anterior, defina:

```bash
export DATABASE_ADMIN_URL=postgresql://postgres:dev_local_change_me@localhost:5432/postgres
# PowerShell: $env:DATABASE_ADMIN_URL = "postgresql://postgres:dev_local_change_me@localhost:5432/postgres"
```

**Schema e seeds SQL** — a partir da raiz, com a mesma variável:

```bash
python database/run_tests.py
```

**Frontend** — a partir de `frontend/`:

```bash
npm test
npm run lint
npm run build
```

| Verificação | O que cobre |
|---|---|
| Pytest | Serviços, repositórios, rotas, autenticação, parser, IA, validação, duplicatas, limpeza e minimização de dados. |
| Testes SQL | Schema, restrições, índices e seeds. |
| Node Test Runner | Serviços utilitários do frontend. |
| ESLint | Análise estática do código JavaScript/React. |
| Vite Build | Build de produção do frontend. |

## Estrutura do repositório

```text
cin-event-hub/
├── backend/
│   ├── app/
│   │   ├── api/                 # Routers FastAPI: auth, eventos e extração
│   │   ├── core/                # Configuração, dependências e segurança
│   │   ├── database/            # Engine e sessão SQLAlchemy
│   │   ├── models/              # Models ORM
│   │   ├── repositories/        # Consultas e persistência
│   │   ├── schemas/             # Contratos Pydantic
│   │   └── services/            # Regras de negócio e integrações
│   ├── scripts/                 # Scripts operacionais
│   └── tests/                   # Testes do backend
├── database/
│   ├── 001_schema.sql           # Schema relacional
│   ├── 002…005_seed_*.sql       # Dados de demonstração
│   ├── tests/                   # Testes de schema e seeds
│   └── run_tests.py             # Executor da suíte SQL
├── docs/                        # Documentação do projeto (veja o índice em docs/README.md)
├── frontend/
│   ├── public/                  # Recursos estáticos
│   ├── tests/                   # Testes do frontend
│   └── src/
│       ├── components/          # Componentes reutilizáveis
│       ├── contexts/            # Contextos React
│       ├── hooks/               # Hooks
│       ├── pages/               # Páginas públicas e administrativas
│       ├── routes/              # Proteção de rotas
│       ├── services/            # Integração com a API
│       └── styles/              # Estilos
├── docker-compose.yml
└── README.md
```

## Documentação

O índice completo está em [`docs/README.md`](docs/README.md). Os principais documentos:

| Documento | Conteúdo |
|---|---|
| [Visão de arquitetura](docs/architecture/overview.md) | Componentes, camadas e fluxo de extração em detalhe. |
| [Modelo de dados](docs/architecture/data-model.md) | Tabelas, relacionamentos e restrições atuais. |
| [ADRs](docs/adr/README.md) | Decisões de arquitetura, alternativas e consequências. |
| [Desenvolvimento local](docs/operations/local-development.md) | Ambiente, variáveis e execução passo a passo. |
| [Prontidão para produção](docs/operations/production-readiness.md) | Verificações pendentes antes de uma implantação pública. |
| [Estratégia de testes](docs/testing/strategy.md) | Suítes, comandos e limites dos testes. |
| [Contribuição](docs/workflow/contributing.md) | Branches, pull requests e convenções. |
| [Backlog](docs/requirements/backlog/Backlog_v4.pdf) | Épicos, histórias de usuário e critérios de aceite (versão vigente). |
| [Diagramas C4 e UML](docs/architecture/diagrams/) | Contexto, contêineres e implantação, como definidos nas entregas. |
| [Migração para PostgreSQL](docs/architecture/database/migracao-postgresql.md) | Decisões e etapas da migração do banco. |
| [Refatoração do banco](docs/architecture/database/refatoracao-banco.md) | Decisões do schema, trade-offs e seeds. |
| [Minimização de dados (LGPD)](docs/reports/technical/lgpd-minimizacao-dados.md) | Dados persistidos a partir dos e-mails e limites da minimização. |
| [Paginação de eventos](docs/reports/technical/paginacao-eventos.md) | Contrato de `GET /events`. |
| [Relatórios de testes](docs/reports/testing/README.md) | Roteiro, registros e relatórios de execução. |
| [Guia para contribuidores](docs/guides/contribuidores-docker.pdf) | Ambiente de desenvolvimento e comandos essenciais. |
| [Integração com o OpenRouter](docs/guides/integracao-openrouter-execucao-local.pdf) | Configuração da IA e execução local. |
| [Entregas e slides](docs/reports/deliveries/) | Relatórios e apresentações submetidos na disciplina. |

## Equipe e contribuições

Os papéis foram informados pela equipe; as contribuições foram resumidas a partir do histórico de Pull Requests e não medem produtividade individual.

| Integrante | Papel no projeto | Principais contribuições |
|---|---|---|
| **Bruno Silva** · [@SilvaaBruno](https://github.com/SilvaaBruno) | **Scrum Master · Gerente de Projeto · Desenvolvedor Full Stack · Engenheiro de Dados · Documentação Técnica** | Organização e acompanhamento do trabalho; documentação do projeto (relatórios, apresentações, guias técnicos e README); telas iniciais de login e criação de eventos; testes do frontend; schema e seeds SQL; migração do backend para PostgreSQL; paginação da API; minimização de dados pessoais nos logs. PRs: [#2](https://github.com/lacavaalex/cin-event-hub/pull/2), [#3](https://github.com/lacavaalex/cin-event-hub/pull/3), [#9](https://github.com/lacavaalex/cin-event-hub/pull/9), [#10](https://github.com/lacavaalex/cin-event-hub/pull/10), [#17](https://github.com/lacavaalex/cin-event-hub/pull/17), [#18](https://github.com/lacavaalex/cin-event-hub/pull/18), [#19](https://github.com/lacavaalex/cin-event-hub/pull/19), [#20](https://github.com/lacavaalex/cin-event-hub/pull/20), [#21](https://github.com/lacavaalex/cin-event-hub/pull/21). |
| **Alex Lacava** · [@lacavaalex](https://github.com/lacavaalex) | Backend · Integrações · IA | Motor de extração via Gmail, parser heurístico, fallback de IA via OpenRouter, validação autônoma, detecção de lembretes duplicados, prompt de extração e melhorias da experiência pública. PRs: [#11](https://github.com/lacavaalex/cin-event-hub/pull/11), [#13](https://github.com/lacavaalex/cin-event-hub/pull/13), [#15](https://github.com/lacavaalex/cin-event-hub/pull/15), [#27](https://github.com/lacavaalex/cin-event-hub/pull/27), [#28](https://github.com/lacavaalex/cin-event-hub/pull/28). |
| **Albert Santana** · [@albertsantanadev](https://github.com/albertsantanadev) | Full Stack · DevOps | Edição e exclusão de eventos, favoritos, conteinerização e deploy, identidade inicial da aplicação. PRs: [#7](https://github.com/lacavaalex/cin-event-hub/pull/7), [#8](https://github.com/lacavaalex/cin-event-hub/pull/8), [#30](https://github.com/lacavaalex/cin-event-hub/pull/30). |
| **Wallyson Rodrigues** · [@ExeWall](https://github.com/ExeWall) | Backend · Segurança · Qualidade | Autenticação JWT e criação de eventos; expiração e limpeza agendada; refatoração da entidade usuário conforme o EER; roteiro de testes; padronização do fuso de Recife. PRs: [#4](https://github.com/lacavaalex/cin-event-hub/pull/4), [#16](https://github.com/lacavaalex/cin-event-hub/pull/16), [#23](https://github.com/lacavaalex/cin-event-hub/pull/23), [#29](https://github.com/lacavaalex/cin-event-hub/pull/29), [#31](https://github.com/lacavaalex/cin-event-hub/pull/31). |
| **Erlon Matheus** · [@emfs2-byte](https://github.com/emfs2-byte) | Frontend · UX · Identidade visual | Logout, listagem e detalhes de eventos, busca e paginação, filtros, integração com agenda, painel de status da extração, temas claro e escuro, revisão da identidade visual. PRs: [#6](https://github.com/lacavaalex/cin-event-hub/pull/6), [#12](https://github.com/lacavaalex/cin-event-hub/pull/12), [#14](https://github.com/lacavaalex/cin-event-hub/pull/14), [#22](https://github.com/lacavaalex/cin-event-hub/pull/22), [#32](https://github.com/lacavaalex/cin-event-hub/pull/32). |
| **José Romildo** · [@joseromildo0](https://github.com/joseromildo0) | Banco de Dados · Modelagem Relacional | Modelagem do banco, schema relacional, seeds e integração entre schema e models do backend. PR: [#25](https://github.com/lacavaalex/cin-event-hub/pull/25). |

## Limitações conhecidas

- **Favoritos:** identificados apenas por `X-User-Id`, sem autenticação de usuário final, e ainda sem jornada completa no frontend (veja o aviso na seção [API](#api)).
- **Docker Compose:** o `docker-compose.yml` ainda não aplica o `001_schema.sql` nem repassa as variáveis de administrador e de OAuth do Gmail usadas pelo backend, e o `HEALTHCHECK` do backend consulta `/health`, rota que não existe (a verificação é `GET /`). A execução documentada é a local.
- **Tipos de evento:** o banco aceita `Palestra`, `Workshop`, `Hackathon` e `Outro`; o frontend ainda lista também um filtro "Minicurso", sem correspondência no schema.
- **Produção:** antes de uma implantação pública, restringir o CORS (hoje aberto a qualquer origem), revisar a gestão de segredos e as credenciais OAuth, definir a política de autenticação de usuários finais e adicionar observabilidade.
- **LGPD:** a minimização de dados reduz a exposição, mas não equivale a uma auditoria jurídica nem a uma certificação de conformidade.

---

<div align="center">

**CIn Event Hub** · IESI 2026.2 · CIn-UFPE

*Tecnologia para aproximar a comunidade acadêmica das oportunidades que acontecem no CIn.*

[Repositório](https://github.com/lacavaalex/cin-event-hub) · [Issues](https://github.com/lacavaalex/cin-event-hub/issues) · [Pull Requests](https://github.com/lacavaalex/cin-event-hub/pulls)

</div>
