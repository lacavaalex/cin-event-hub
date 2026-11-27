# Guia de Q&A — Hub de Eventos CIn

Respostas baseadas na documentação e no código da `develop` (commit `c131e9d`). Quando algo for hipótese ou limitação, diga isso.

## Pontos de atenção na defesa
- **ASCOM não aparece nos documentos do repositório.** Trate como hipótese a validar. Não afirme dores ou responsabilidades dela.
- **A extração foi testada com Gmail e Gemini simulados.** Não há corpus real de e-mails nem a métrica de acerto > 90% da US 4.2 medida.
- **Tailwind e TypeScript:** as Entregas 3 e 4 citam Tailwind, mas ele não está nas dependências do front. O front é React + Vite em JavaScript. O back-end foi feito em Python justamente "em detrimento do TypeScript". Não cite Tailwind nem TypeScript como usados.
- **Números dos slides** (291 / 106 / 83) vêm do registro de testes e do relatório de ponta a ponta feitos na `develop`. Esses arquivos não estão no repositório; coloque-os em `docs/` se quiser citá-los com fonte.
- **Dados da demo são fictícios** (seed do banco).

## 1. Problema e stakeholders

**Como identificaram o problema?** Pela observação do próprio ambiente: o CIn divulga eventos por disparos de e-mail para as contas institucionais, e o volume de mensagens faz o aluno perder o que importa (Entrega 1). Não houve pesquisa formal com alunos; o backlog prevê validar páginas e dados com uma parcela de alunos (Entrega 4).

**Por que é relevante?** O ecossistema de eventos do CIn (palestras, workshops, hackathons) traz networking e aprendizado. Se o aluno não vê o evento, a oportunidade se perde.

**Quem se beneficia?** Alunos (consulta unificada), curadoria (painel e publicação automática) e o CIn. A ASCOM é hipótese: a solução poderia dar visibilidade à divulgação, mas isso precisa ser confirmado com ela.

**Como as necessidades dos stakeholders foram consideradas?** Alunos: listagem, busca, filtro, detalhes, `.ics` e favoritos. Curador: login e CRUD de eventos. Instituição: LGPD (minimização) e custo zero. ASCOM: ainda não consultada.

**Por que a solução é adequada?** Ataca a causa (e-mail desestruturado) sem pedir mudança de hábito de quem divulga: o evento continua saindo por e-mail e o sistema o organiza.

## 2. Produto e regras de negócio

**Funcionalidades essenciais?** Listar, filtrar, buscar e detalhar eventos; exportar `.ics`; login do curador; CRUD de eventos; extração automática de e-mails; exclusão automática de eventos vencidos.

**Regras principais?**
- Evento só é publicado se tiver título, data, hora e local; data no passado é descartada (validação em America/Recife).
- Evento vencido some do site; o painel mostra "Encerrado" até a limpeza diária (03:00).
- E-mail já processado não é lido de novo (idempotência pelo identificador da mensagem).
- Paginação: `GET /events` com `page` e `page_size` (máximo 100).
- Rotas de escrita exigem JWT de administrador (401 sem token válido, 403 sem permissão).

**O que foi priorizado no MVP?** Os Must do backlog v4 (MoSCoW): login, CRUD, listagem, detalhes, extração com IA e validação autônoma, exclusão automática e favoritos.

**O que ficou fora e por quê?** Notificações por interesse (o e-mail institucional já avisa e uma web app não tem push nativo); login de aluno (favoritos usam um identificador anônimo no navegador); hora de término (assume-se 1 h no `.ics`).

**Limitações que ainda existem?**
- Sem desduplicação por conteúdo: um "Lembrete: …" do mesmo evento vira outro card (US 4.5, ainda fora da `develop`).
- Se o Gemini falha, o e-mail fica como erro e não é reprocessado (US 4.6).
- Só os 50 e-mails mais recentes da janela são lidos por ciclo (`GMAIL_MAX_RESULTS`, sem paginação).
- A Home exibe só os 100 primeiros eventos.
- A descrição extraída pelo parser pode começar com a saudação do e-mail.
- Token expirado no painel mostra erro genérico, sem voltar ao login.
- A ★ de favoritos não é renderizada; "Meus Favoritos" e "Status de Extração" são placeholders.

## 3. Decisões técnicas

| Decisão | Por quê (necessidade) | Alternativas | Critério |
|---|---|---|---|
| **Três camadas, monólito** | Escopo enxuto e tráfego baixo; microsserviços seriam excesso de infraestrutura. Front nunca acessa o banco. | Microsserviços | Simplicidade proporcional ao problema; porta aberta para evoluir (Entrega 3) |
| **Python + FastAPI** | Integração direta com Gmail API e com a IA; API REST rápida de escrever e tipada. | Node.js/Express, TypeScript | Ecossistema de bibliotecas para Gmail e Gemini (Entrega 3) |
| **React + Vite (SPA)** | Navegação fluida e roteamento dinâmico para a listagem e o painel. | Páginas renderizadas no servidor | Responsividade e desenvolvimento em paralelo com o back-end |
| **PostgreSQL 16** | Entidades previsíveis, com relações e restrições (FKs, CHECKs). | SQLite, arquivos locais | Integridade referencial nativa; a migração de SQLite para PostgreSQL está em `docs/db/migracao-postgresql.md` |
| **Gmail API com OAuth 2.0** | Acessar a caixa institucional sem guardar senha. | Apps Script, Pub/Sub, IMAP | Menor complexidade de implantação (Entrega 1 e 3) |
| **Parser primeiro, Gemini depois** | Reduz chamadas à IA e custo; a IA cobre só o texto livre. Registros mostram qual caminho foi usado (`processado` ou `processado_ia`). | Só IA | Custo zero no free tier |
| **Chaves só no servidor** | Credenciais do Gmail e da IA não podem chegar ao navegador. | Chamar APIs do front | Segurança (Entrega 3) |
| **Minimização LGPD** | O e-mail traz dados pessoais irrelevantes ao evento. Remetente vira domínio; e-mail, CPF e telefone são mascarados nos registros. | Guardar o e-mail inteiro | DoD D8 (`docs/dev_notes/lgpd-minimizacao-dados.md`) |

**Como organiza responsabilidades?** `api` (rotas) → `services` (regras) → `repositories` (acesso a dados) → `models`/`schemas`. A extração vive só dentro da camada de aplicação.

**Como as partes se comunicam?** Front → API REST (JSON) → PostgreSQL. O agendador (APScheduler) roda dentro do back-end e dispara extração (a cada 12 h por padrão) e limpeza (diária, 03:00).

**Como os dados são armazenados?** Tabelas `events`, `usuario`, `extracao` (logs), `favorito`. Favoritos apagam em cascata com o evento; o log da extração mantém o registro com `event_id` nulo.

**Segurança, validação e erros?** Senha com hash (bcrypt), JWT HS256 com expiração configurável (60 min por padrão), validação com Pydantic (422 em entradas inválidas), erros de extração registrados por status (`erro`, `ignorado`, `extracao_incompleta`). CORS está aberto (`*`): é um ponto a restringir antes de produção.

## 4. Evolução

**O que falta para uso real?** Restringir o CORS, definir segredos fora do repositório, terminar Docker/deploy, validar a extração com e-mails reais anonimizados, e conversar com a ASCOM.

**Próximos passos?** US 4.5 (desduplicação), US 4.6 (retentativa), ★ de favoritos na tela, tela de status da extração, paginação na Home.

**Como evoluir?** Se o volume crescer, separar o worker de extração do servidor da API; hoje o monólito basta.

**Riscos?** Qualidade da extração com e-mails reais (R2), acesso à caixa institucional (R3) e custo/cota da IA. O backlog v4 lista os riscos R1–R5.

## Perguntas difíceis

- **"Isso foi testado com e-mails reais?"** Não com corpus real. Foi testado com Gmail e Gemini simulados, em 83 casos de jornada. O próximo passo é rodar um corpus rotulado de pelo menos 30 e-mails anonimizados.
- **"A ASCOM pediu isso?"** Não temos esse registro nos documentos. Tratamos a ASCOM como hipótese e queremos validar.
- **"Por que não TypeScript no back-end?"** Python facilita o uso nativo da Gmail API e do modelo de IA (Entrega 3). O front está em JavaScript.
- **"E se o Gemini errar?"** Há validação autônoma (campos e data futura) antes de publicar, e o parser resolve os e-mails bem formatados sem IA. Se a IA falhar, hoje o e-mail fica como erro (retentativa é a US 4.6).
- **"Dados pessoais?"** Só o domínio do remetente fica no registro; e-mail, CPF e telefone são mascarados. Resta uma lacuna: um contato escrito no 1º parágrafo do e-mail pode aparecer na descrição publicada. Está registrado como decisão em aberto (L2) no documento de LGPD.
