# Desenvolvimento local e operação básica

Este guia descreve uma execução de desenvolvimento com PostgreSQL local, backend FastAPI e frontend React. Foi escrito a partir das configurações rastreadas no repositório em 27/11/2026.

## 1. Pré-requisitos

| Ferramenta | Versão de referência | Uso |
|---|---:|---|
| Python | 3.12 | Backend e testes. |
| Node.js | 20 ou superior | Frontend e testes. |
| PostgreSQL | 13 ou superior | Banco de dados. O Compose usa PostgreSQL 16. |
| Git | Atual | Clonar o repositório e trabalhar com branches. |
| Docker | Opcional | Executar PostgreSQL em container. |

## 2. Preparar o banco

Na raiz do repositório, suba uma instância local de PostgreSQL. A senha abaixo é exclusivamente ilustrativa para desenvolvimento local; não reutilize em ambientes compartilhados.

```bash
docker run --name cin-event-hub-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=dev_local_change_me \
  -e POSTGRES_DB=cin_event_hub \
  -p 5432:5432 \
  -d postgres:16-alpine
```

Aplique o schema oficial:

```bash
psql -h localhost -U postgres -d cin_event_hub \
  -v ON_ERROR_STOP=1 -f database/001_schema.sql
```

Opcionalmente, carregue os dados de demonstração:

```bash
psql -h localhost -U postgres -d cin_event_hub \
  -v ON_ERROR_STOP=1 -f database/002_seed_eventos.sql
```

Os demais seeds são opcionais e devem ser aplicados na ordem indicada pelo script `database/run_tests.py`: usuários, extrações e favoritos.

## 3. Configurar o backend

```bash
cd backend
```

Crie o ambiente virtual e instale dependências:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements-dev.txt
```

Copie o exemplo e edite o arquivo privado:

```powershell
Copy-Item .env.example .env
```

No macOS/Linux:

```bash
cp .env.example .env
```

Configuração mínima para subir a API:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:dev_local_change_me@localhost:5432/cin_event_hub
SECRET_KEY=COLOQUE_UMA_CHAVE_FORTE_COM_PELO_MENOS_32_CARACTERES
ADMIN_EMAIL=admin@exemplo.local
ADMIN_PASSWORD=troque-esta-senha-local
ADMIN_NAME=Administrador
ADMIN_PROFILE_NAME=admin
```

Gere uma chave localmente, sem reutilizar o exemplo:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

O backend aceita `JWT_SECRET_KEY` como alias com precedência sobre `SECRET_KEY`. A aplicação exige chave com pelo menos 32 caracteres. O administrador inicial é criado se `ADMIN_EMAIL` e `ADMIN_PASSWORD` estiverem configurados juntos e o e-mail ainda não existir; um usuário comum existente não é promovido automaticamente.

Inicie a API dentro da pasta `backend`:

```bash
uvicorn app.main:app --reload
```

A documentação interativa da API fica em `http://localhost:8000/docs`. O endpoint de saúde efetivamente implementado é `GET /` e retorna `status: ok`.

## 4. Configurar integrações opcionais

### Gmail API

A extração exige arquivos OAuth 2.0 de aplicativo desktop e token local:

```dotenv
GMAIL_CREDENTIALS_FILE=./gmail_credentials.json
GMAIL_TOKEN_FILE=./gmail_token.json
GMAIL_QUERY=newer_than:7d
GMAIL_MAX_RESULTS=50
EXTRACTION_ENABLED=true
EXTRACTION_INTERVAL_MINUTES=720
```

Configure o projeto no Google Cloud, habilite a Gmail API e baixe o arquivo de credenciais OAuth de aplicativo desktop. Salve-o no caminho indicado por `GMAIL_CREDENTIALS_FILE`. Na primeira autorização, o fluxo `InstalledAppFlow.run_local_server` solicita consentimento e grava o token em `GMAIL_TOKEN_FILE`. Esse bootstrap foi pensado para um ambiente local com navegador; não presuma que o fluxo interativo funcionará diretamente em um container/servidor remoto.

O escopo utilizado pelo cliente é `https://www.googleapis.com/auth/gmail.readonly`. As credenciais e o token não devem ser versionados. O `.gitignore` já exclui padrões desses arquivos.

### OpenRouter

O fallback de IA pode ser configurado com:

```dotenv
OPENROUTER_API_KEY=sua-chave
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
GEMINI_MODEL=google/gemma-4-31b-it:free
GEMINI_MAX_OUTPUT_TOKENS=1024
```

O código usa o SDK Python `openai` para chamar o endpoint compatível com OpenAI do OpenRouter. `GEMINI_API_KEY` ainda existe como fallback de compatibilidade no código/configuração. O nome `GEMINI_MODEL` é o nome da variável de configuração do modelo e pode conter o identificador do modelo aceito pelo OpenRouter.

**Privacidade:** quando o parser heurístico não consegue extrair os campos obrigatórios, o fallback envia o assunto e o corpo do e-mail ao provedor configurado. A máscara aplicada aos logs não remove esses dados do conteúdo transmitido. Não use mensagens institucionais reais sem avaliar previamente autorização, política de retenção e condições do provedor.

## 5. Configurar e iniciar o frontend

Em outro terminal:

```bash
cd frontend
npm ci
```

Crie `frontend/.env` com a URL da API:

```dotenv
VITE_API_URL=http://localhost:8000
```

Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

O Vite informa a URL local, normalmente `http://localhost:5173`.

## 6. Executar testes e verificações

Execute cada suíte contra um banco PostgreSQL de teste separado. **Não aponte as variáveis de testes para uma base compartilhada ou de produção.**

### Banco de dados

Na raiz do repositório:

```bash
pip install "psycopg[binary]"
python database/run_tests.py
```

O script cria e remove bancos temporários chamados `iesi_test_schema`, `iesi_test_seed` e `iesi_test_seeds`. O usuário PostgreSQL precisa poder criar e remover bancos. A URL administrativa pode ser informada em `DATABASE_ADMIN_URL`.

### Backend

Na pasta `backend`, com dependências de desenvolvimento instaladas:

```bash
python -m pytest
```

A fixture cria um banco temporário chamado `iesi_test_backend`, aplica `database/001_schema.sql`, limpa as tabelas entre testes e remove o banco no encerramento. O usuário do PostgreSQL precisa ter permissão para criar/remover bancos. Use `DATABASE_ADMIN_URL` para apontar explicitamente ao servidor de teste.

### Frontend

Na pasta `frontend`:

```bash
npm test
npm run lint
npm run build
```

O script `npm test` usa o runner nativo `node --test` nos testes de serviços.

## 7. Execução manual da extração

Com backend, banco e autenticação administrativa configurados, faça login em `POST /auth/login` e use o token retornado no cabeçalho `Authorization: Bearer <token>` para chamar `POST /extraction/run`. A rota dispara um ciclo manual e pode iniciar o fluxo OAuth interativo do Gmail se ainda não houver token autorizado.

O painel administrativo consulta `GET /extraction/status` e `GET /extraction/alerts`. Essas rotas exigem JWT de administrador.

## 8. Atenção ao Docker Compose atual

O `docker-compose.yml` está versionado, mas **não deve ser tratado como um caminho de inicialização validado sem revisão adicional**. No estado analisado:

- o Compose injeta `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET` e `GMAIL_REFRESH_TOKEN`, enquanto o cliente atual lê `GMAIL_CREDENTIALS_FILE` e `GMAIL_TOKEN_FILE`;
- o Compose injeta `ALLOWED_ORIGINS`, mas `backend/app/main.py` ainda configura `allow_origins=["*"]` diretamente;
- o Dockerfile do backend verifica `/health`, mas a API atual expõe o health check em `/`;
- o arquivo Compose descreve variáveis de um fluxo de deploy anterior e precisa ser alinhado com os arquivos `.env.example` atuais.

Esses pontos estão listados em [prontidão para produção](production-readiness.md). Até a correção e validação de ponta a ponta, prefira os passos explícitos deste guia para desenvolvimento local.

## 9. Encerrar e preservar dados

- `docker stop cin-event-hub-db` interrompe o banco local sem apagar os dados.
- `docker start cin-event-hub-db` inicia o mesmo container novamente.
- `docker rm -f cin-event-hub-db` remove o container; dados persistidos na camada do container podem ser perdidos se não houver volume dedicado.
- Não use `docker compose down -v` ou comandos de remoção de volumes sem confirmar que o banco não contém dados necessários.
