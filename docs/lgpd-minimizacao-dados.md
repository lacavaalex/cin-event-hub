# LGPD: minimização dos dados extraídos dos e-mails (IESI-60)

**Task:** IESI-60 — *US 4.1 a 4.6: [LGPD/Segurança] Revisar logs e banco para garantir minimização de dados extraídos dos e-mails.*
**Critério:** DoD **D8** do Backlog v3 — *"nenhum dado pessoal irrelevante é persistido; e-mails processados só contribuem com dados pertinentes aos eventos"*. Risco **R3**: o backend lê a caixa institucional.

## 1. Resultado da revisão (o que o backend grava de cada e-mail)

| Onde | O que vinha do e-mail | Situação antes | Situação agora |
|------|----------------------|----------------|----------------|
| `extraction_logs.gmail_message_id` | id da mensagem no Gmail | necessário (idempotência da varredura); não é dado pessoal | **mantido** |
| `extraction_logs.source_email` | **endereço completo do remetente** (`maria.souza@cin.ufpe.br`) | dado pessoal sem relação com o evento; também exposto em `GET /extraction/alerts` | **só o domínio** (`cin.ufpe.br`); sem endereço válido, `desconhecido` |
| `extraction_logs.extracted_data` | campos extraídos (título, descrição, local, link) | podia conter e-mail, telefone e CPF do texto | **e-mail, CPF e telefone mascarados** (`[e-mail]`, `[cpf]`, `[telefone]`) |
| `extraction_logs.error_message` | mensagem da exceção (ex.: Gemini devolvendo JSON inválido ecoa trecho da resposta) | podia carregar trechos do e-mail | **mascarada** antes de cortar em 500 caracteres |
| `events` (título, descrição, local, link) | dados do evento | dado **pertinente ao evento** (D8 permite) | **mantido sem alteração** (ver 3) |
| corpo do e-mail e assinatura | — | nunca gravados (a descrição é só o 1º parágrafo) | **continua assim**; agora há teste que varre o banco inteiro |
| `extracao.input_text` / `extracao.prompt` (schema do José) | poderiam guardar o corpo/prompt | o backend **não escreve** nessa tabela | **sem mudança**; teste garante que fica vazia (ver 4) |
| log do agendador (`logging`) | só contagens | sem dado pessoal | sem mudança |

## 2. O que foi alterado

| Arquivo | Mudança |
|---------|---------|
| `backend/app/services/extracao_email/minimizacao.py` | **Novo.** `dominio_do_remetente()` e `mascarar_dados_pessoais()` |
| `backend/app/services/extracao_email/extraction_service.py` | `_log` (único ponto que grava o log) passa o remetente por `dominio_do_remetente`, mascara `extracted_data` e `error_message`; `_short` mascara **antes** de cortar em 500 (não sobra pedaço de e-mail) |
| `backend/app/models/extraction_log.py` | só o comentário da classe (descreve a minimização) |
| `backend/tests/test_minimizacao_lgpd.py` | **Novo.** 33 testes, sem depender de recurso de um banco específico (rodam em SQLite e em PostgreSQL) |
| `docs/lgpd-minimizacao-dados.md`, `docs/refatoracao-banco.md` | documentação |

Não há mudança de schema, de coluna, de rota nem de contrato da API (`source_email` continua string).

### Máscaras

| Dado | Exemplo | Vira |
|------|---------|------|
| e-mail | `ana.lima+evento@gmail.com` | `[e-mail]` |
| CPF (com ou sem pontuação) | `123.456.789-09`, `12345678909` | `[cpf]` |
| telefone BR | `(81) 99999-8888`, `+55 81 99999-8888`, `99999-8888` | `[telefone]` |

Propositalmente **não** mascara datas, horas, links nem intervalos como `2025-2026` (há testes para isso). Telefone fixo sem DDD (`3333-4444`) também não é mascarado, porque se confunde com intervalo de anos.

## 3. Decisões

| # | Decisão | Por quê |
|---|---------|---------|
| L1 | Remetente vira domínio, sem mudar a coluna | O admin ainda vê a origem (`cin.ufpe.br`); o schema do José nem tem coluna de remetente, então seguir nessa direção não conflita com ele |
| L2 | Mascarar só o **log** (`extracted_data`, `error_message`), não o evento publicado | O evento é o dado pertinente (D8) e mexer nele mudaria o resultado das US 4.1/4.2/4.4. **Em aberto para o time:** mascarar também a descrição publicada (ex.: um "contato: fulano@gmail.com" no 1º parágrafo aparece na descrição do evento) |
| L3 | Minimizar no `_log`, e não em cada chamada | Ponto único: um caminho novo de log (US 4.5/4.6) já nasce minimizado |
| L4 | Não mexer em `gemini_client.py` | A mensagem de JSON inválido (`cleaned[:200]`) é mascarada ao gravar; não é preciso alterar o código do outro módulo |
| L5 | O texto enviado ao Gemini fica como está | Não é persistência, e o modelo precisa do corpo para extrair o evento. Se o time quiser reduzir (ex.: tirar assinatura antes de enviar), é outra task |

## 4. Sobre o banco (schema do José)

`extracao` tem `input_text` (TEXT, opcional) e `prompt` (TEXT, NOT NULL), que **poderiam** guardar o corpo do e-mail ou o prompt com o corpo. Hoje o backend usa `extraction_logs`, não `extracao` (unificar as duas é decisão em aberto, D6 em `docs/refatoracao-banco.md`). Quando a extração passar a gravar em `extracao`, a recomendação é:

- gravar `body_hash` (já existe, 64 caracteres) em vez do texto; deixar `input_text` **nulo**;
- `prompt`: gravar o **modelo do prompt** (instrução fixa), sem o corpo do e-mail;
- `json_output`: passar pela mesma máscara.

Nada disso foi alterado agora (é tabela de outra pessoa e o backend não a usa). O teste `test_corpo_do_email_nao_vai_para_as_tabelas_extracao_e_email_associado` quebra se alguém começar a gravar lá sem rever este ponto.

## 5. Registros que já estão no banco

O código novo só minimiza o que for gravado daqui para frente. Para o que já existe em `extraction_logs` (ambiente com dados reais), rode **uma vez** (é idempotente; testado em PostgreSQL 16; a develop atual ainda usa SQLite, então rode no PostgreSQL de produção/homologação, se houver):

```sql
-- remetente: endereço completo -> domínio
UPDATE extraction_logs
SET source_email = COALESCE(NULLIF(lower(substring(source_email from '@([^>\s]+)')), ''), 'desconhecido')
WHERE source_email LIKE '%@%';

-- e-mails dentro das mensagens de erro
UPDATE extraction_logs
SET error_message = regexp_replace(error_message, '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+', '[e-mail]', 'g')
WHERE error_message LIKE '%@%';
```

Só e-mails são tratados nos registros antigos; telefone e CPF em `extracted_data` antigo exigiriam revisão manual.

## 6. Testes

`python -m pytest tests/test_minimizacao_lgpd.py -v` (dentro de `backend/`):

| Ambiente | Testes da IESI-60 | Suíte completa |
|----------|-------------------|----------------|
| develop atual (SQLite em memória) | 32 passed, 1 skipped | **111 passed, 1 skipped** |
| com migração + schema do José (PostgreSQL ligado) | **33 passed** | **144 passed** (sem `google-genai` instalado: 142 passed e 2 skipped, os dois testes do Gemini) |

O teste que fica *skipped* na develop atual é o que confere que `extracao` e `email_associado` continuam vazias; essas tabelas só existem no schema PostgreSQL.

| Grupo | O que prova |
|-------|-------------|
| `dominio_do_remetente` (8 casos) | `Nome <a@b>`, caixa alta, sem `@`, vazio, `None` |
| máscaras (9 casos) + não-alterações (7 casos) | mascara e-mail/CPF/telefone; não toca em data, hora, link, `2025-2026` |
| log do parser / alerta do admin | `source_email` só com domínio, inclusive no schema de `GET /extraction/alerts` |
| `extracted_data` | descartado pela validação: dados pessoais mascarados, dados do evento legíveis |
| `error_message` | exceção do Gemini com e-mail/telefone sai mascarada; continua ≤ 500; o ignorado da US 4.1 mantém o texto |
| **varredura do banco** | e-mail com assinatura (nome, Gmail, telefone, CPF) → evento extraído, mas **nenhuma** coluna de texto/JSON de **nenhuma** tabela contém a assinatura nem o endereço do remetente |
| `extracao`/`email_associado` | continuam vazias depois da extração |

Contraprova feita: sem a mudança em `extraction_service.py`, 6 desses testes falham.
