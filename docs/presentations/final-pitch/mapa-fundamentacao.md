# Mapa de fundamentação — o que cada afirmação dos slides sustenta

Legenda: **D** = documentado · **V** = verificado no código/execução · **H** = hipótese (não documentada).

| Slide | Afirmação | Tipo | Fonte verificada |
|---|---|---|---|
| 1 | Equipe de seis pessoas | D | `docs/entregas/pdf/IESI_Entrega_1.pdf` (lista de integrantes) |
| 2 | Eventos divulgados por disparos de e-mail para contas `@cin.ufpe.br` | D | Entrega 1, "Descrição do Problema" |
| 2 | Alto volume com vendas de usados, achados e perdidos e avisos das turmas | D | Entrega 1 e Entrega 2 (Sobrecarga e Poluição) |
| 2 | O aluno perde eventos e falta visão de longo prazo | D | Entrega 2, "Identificação de Problemas e Necessidades" |
| 2 | Ilustração da caixa de entrada | — | Representação gráfica do cenário; não é captura real (legenda no slide) |
| 3 | Alunos são o usuário final | D | Entrega 4, "Envolvimento de Usuários" |
| 3 | CIn tem ecossistema ativo de eventos, com networking e aprendizado | D | Entrega 1 |
| 3 | **ASCOM** como stakeholder com necessidade de divulgação | **H** | Não consta em `docs/` nem nas entregas; definida no enunciado do pitch. Selo "A validar" no slide |
| 4 | Gmail API com OAuth 2.0 | V | `backend/app/services/extracao_email/gmail_client.py` |
| 4 | Parser estruturado + Gemini | V | `extracao_email/parser.py`, `services/ia_gemini/gemini_client.py`, `extraction_service.py` (`processado` / `processado_ia`) |
| 4 | Validação de campos obrigatórios e data futura (America/Recife) | V | `services/validacao/validation_service.py`, `parser.py` (`REQUIRED_FIELDS`) |
| 4 | Dados em PostgreSQL | V | `database/001_schema.sql`, `backend/requirements.txt` (`psycopg`) |
| 4 | Extração a cada 12 h por padrão | V | `backend/app/core/config.py` (`EXTRACTION_INTERVAL_MINUTES = 720`), `extracao_email/scheduler.py` |
| 4 | Do remetente fica só o domínio; e-mail, CPF e telefone mascarados nos registros | V | `extracao_email/minimizacao.py`; `docs/dev_notes/lgpd-minimizacao-dados.md` |
| 4 | Limpeza diária às 03:00 (Recife) | V | `services/events/cleanup_scheduler.py`; `config.py` (`CLEANUP_CRON_HOUR = 3`) |
| 5 | Lista cronológica, busca e filtro por tipo | V | `frontend/src/pages/Home.jsx`; captura da Home |
| 5 | Detalhes e exportação `.ics` | V | `frontend/src/pages/EventDetails.jsx`; US 3.4 e 3.5 do Backlog v4 |
| 5 | Login do curador e CRUD de eventos | V | `backend/app/api/auth/router.py`, `api/eventos/router.py`; painel `/admin/events` |
| 5 | Extração testada com Gmail e Gemini simulados | V | Relatório de ponta a ponta (fora do repositório): Gmail e `GeminiClient._generate` simulados |
| 5 | Limpeza automática de vencidos | V | `cleanup_service.py`; testes do backend |
| 5 | Favoritos: API pronta, ★ não aparece | V | `api/eventos/router.py` (`/favorite`, `/favorites`); `FavoriteButton` não é usado em nenhuma página |
| 5 | Status da extração: back-end pronto, tela placeholder | V | `extraction_service.get_status`; `frontend/src/pages/ExtractionStatusPage.jsx` |
| 5 | Home mostra só os 100 primeiros eventos | V | `Home.jsx` pede `pageSize: 100`; `docs/dev_notes/paginacao-eventos.md` |
| 5 | Desduplicação (US 4.5) e retentativa (US 4.6) planejadas | D | Backlog v4 (US 4.5 Should, US 4.6 Could); US 4.5 está em branch própria, fora da `develop` |
| 5 | Docker em revisão | V | PR aberto da branch `feat/Dockerização-Deploy` |
| 6 | Três camadas, monólito, sem microsserviços | D | Entrega 3, "Arquitetura de Aplicações" |
| 6 | Python escolhido em vez de TypeScript no back-end | D | Entrega 3, "Arquitetura Tecnológica" |
| 6 | PostgreSQL por integridade referencial | D/V | Entrega 3; `database/001_schema.sql` (FKs e CHECKs) |
| 6 | Parser primeiro, IA depois | V | `extraction_service.py` (docstring do fluxo) |
| 6 | Chaves só no servidor | D/V | Entrega 3; `config.py` lê variáveis de ambiente |
| 6 | Minimização LGPD | V | `docs/dev_notes/lgpd-minimizacao-dados.md` |
| 7 | 291 testes de backend | V | `REGISTRO_TESTES_cin-event-hub.md` (fora do repositório): `291 passed` |
| 7 | 106 verificações de banco | V | Mesmo registro (testes do banco, 106 ok) |
| 7 | 83 casos de jornada, 12 defeitos | V | `RELATORIO_E2E_develop.md` (fora do repositório): 83 executados, 12 ❌ do roteiro |
| 7 | Captura da Home com dados de demonstração | V | Captura real do front local com `database/002_seed_eventos.sql` |
| 8 | Próximos passos | D | Backlog v4 (US 4.5, 4.6, 6.1, 6.2, 4.3); Sprint 4 (Docker) |

## Itens das entregas que **não** foram usados por não se confirmarem no código
- **Tailwind CSS** (Entrega 3 e 4): não está em `frontend/package.json`.
- **TypeScript**: o front é JavaScript (`.jsx`) e o back-end é Python.
- **Painel para "revisão de e-mails extraídos"** (Entrega 3): não há esse fluxo; a validação é autônoma (US 4.4).

## Fontes lidas
`docs/entregas/pdf/` (Entregas 1–4), `docs/backlog/Backlog_v4.pdf`, `docs/dev_notes/`, `docs/db/`, código de `backend/` e `frontend/`, `database/`, PDF-modelo visual "Integração de Dados" e ata da Sprint 4. A transcrição das orientações do professor mencionada no enunciado **não estava acessível**; as regras do pitch foram tiradas do próprio enunciado.
