# Relatório de testes ponta a ponta — `develop` @ `c131e9d`

Jornadas do usuário (Parte D do Roteiro de Testes: INT-xxx e NF-xxx) · cin-event-hub · executado em 22/11/2026

## 1. Resumo

- Casos do roteiro nesta parte: **112** · executados: **88**
- ✅ passou: **67** · ❌ falhou: **12** · ⛔ bloqueado/não executado: **29** · ➖ não se aplica/limitação registrada: **4**
- Fora da contagem acima há 3 casos extras que criei durante a execução (INT-048b ✅, INT-048c ✅, INT-052b ❌), na seção 5. Somando, são 13 ❌ (12 do roteiro + 1 extra).

Legenda: ✅ passou · ❌ defeito · ⛔ não executado/bloqueado · ➖ limitação ou decisão registrada

## 2. Ambiente e método

- Commit testado: `c131e9d` (`origin/develop`) · PostgreSQL 16 local · API FastAPI em `:8000` · front Vite em `:5173` (dev) e `:4173` (build + preview) · navegador Chromium via Playwright.
- **Simulado:** só o serviço do Gmail (lista/mensagens, texto, HTML, multipart, falha de rede) e o `GeminiClient._generate` (respostas por regra, falha forçada). O restante do código real roda: `fetch_new_emails`, `_to_raw_email`, `_html_to_text`, parser, validação, minimização LGPD, agendadores, endpoints. Nenhuma chave foi usada.
- **Relógio:** "hoje" = America/Recife (UTC−3). INT-057, INT-065 e NF-008 usam relógio congelado (freezegun) dentro do processo.
- **Durações reduzidas:** agendadores testados com intervalo de 1 min (≈58 s observados); NF-001 com 30 s de carga em vez do tempo cheio.
- **Dados:** seed da develop; NF-003 com 10 mil eventos, mil usuários e 50 mil favoritos.
- **Limite conhecido:** o front não tem ★ de favoritar (ver D-12); os favoritos foram validados direto pela API.

## 3. Defeitos encontrados (❌)

| # | Gravidade | Casos | Descrição |
|---|---|---|---|
| D-01 | Alta | INT-045 | Sem desduplicação por conteúdo: e-mail e "Lembrete: …" do mesmo evento viram 2 cards (US 4.5 só existe na branch `feature/us-4.5-verificar-duplicacao`). |
| D-02 | Alta | INT-046 | Falha do Gemini fica como `erro` e o e-mail nunca é reprocessado: o evento se perde (US 4.6, retentativa, ausente). |
| D-03 | Alta | INT-052b | `GMAIL_MAX_RESULTS=50` sem paginação: com 60 e-mails na janela, os 10 mais antigos nunca são lidos. |
| D-04 | Alta | INT-027 | Home pede `page_size=100` e não percorre as outras páginas: com 500 eventos só 100 aparecem; a busca por um evento além do 100º dá 0 resultado. |
| D-05 | Média | INT-040 | Descrição do card sai "título + saudação" (ex.: "Palestra de IA Generativa Prezados,"): `_extract_description` usa o 1º parágrafo de `título\ncorpo`. |
| D-06 | Média | INT-048b/c | Consequência de D-05 para LGPD: contato no 1º parágrafo livre iria para o card. Passou nos testes por acaso, não por proteção. |
| D-07 | Média | INT-016, INT-071 | Token expirado, 401 e 403 no painel admin mostram erro genérico, sem redirecionar para /login. |
| D-08 | Média | INT-010, INT-014 | O `.ics` ignora a data/hora de fim (a API não devolve campos de fim). |
| D-09 | Baixa | INT-019 | Mensagens de validação (422) chegam em inglês. |
| D-10 | Baixa | INT-001, INT-096 | README vazio (0 bytes) e sem diagrama C4; `frontend/.env.example` vem com `VITE_USE_MOCK=true` e `VITE_API_URL=:3000`, quem copiar vê dados falsos. |
| D-11 | Baixa | INT-095 | `backend/app/core/Security.py` e `security.py` duplicados; 5 branches remotas abertas. |
| D-12 | Baixa | INT-018/030/031/034 (⛔) | `FavoriteButton` não é renderizado em lugar nenhum; `FavoritesPage` e "Status de Extração" são placeholders. |

Observações sem caso próprio: EventCard mostra o título duas vezes (Link + h3); chip "Minicurso" existe sem tipo correspondente no banco/formulário (decisão H7). A gravidade é minha sugestão; a priorização é do time.

**Correção registrada:** INT-045 foi marcado ✅ na primeira rodada por engano (contei só o título exato) e refeito como ❌.

## 4. Resultado por caso

| ID | Ref. · Pri. · Tipo | Res. | Evidência / observação |
|---|---|---|---|
| INT-001 | D6 · P0 · M | ❌ | GET / = {'status': 'ok', 'project': 'cin-event-hub'}; Home carregou 20 cards com o seed. DEFEITO de documentação: README.md está vazio (0 bytes) e frontend/.env.example vem com VITE_USE_MOCK=true e VITE_API_URL=:3000 — quem copiar o exemplo vê dados falsos. Setup feito por docs/db/migracao-postgresql.md. |
| INT-002 | D6 · P1 · M | ✅ | Front sem back: mensagem 'Não foi possível carregar os eventos' + botão 'Tentar novamente' = True; ao subir a API e clicar no botão a lista voltou = True. Back sem banco: API NÃO sobe (encerra no lifespan); fim do log: ...432 failed: Connection refused \| 	Is the server running on that host and accepting TCP/IP connections? \| (Background on this error at: https://sqlalche.me/e/20/e3q8) \|  \| ERROR:    Application s… |
| INT-003 | D6 · P0 · M | ✅ | Home, login e painel (dev server :5173 → API :8000) sem erro de CORS nem de requisição no console |
| INT-004 | D6 · P0 · M | ✅ | 20 cards iguais após reiniciar a API e depois o PostgreSQL (sem reiniciar a API, pool_pre_ping reconecta) |
| INT-005 | D6 · P0 · M | ✅ | Banco vazio: 'Nenhum evento disponível'; admin criou o 1º evento pelo painel e ele apareceu na Home |
| INT-006 | D6 · P1 · M | ✅ | npm run build (0,95 s; JS 294 kB / 92 kB gzip) + vite preview na 4173 contra a API real: mesma Home do modo dev (20 cards, 'EXIBINDO 1–20 DE 23 EVENTOS'), busca, .ics, login e criação de evento OK |
| INT-007 | D6 · P1 · M | ⛔ | Sem daemon Docker no ambiente; PR do Albert (IESI-85) ainda aberto. Refazer INT-001..005 contra os contêineres após o merge. |
| INT-008 | D6 · P0 · M | ✅ | commit c131e9d · Python 3.13.18 · Node v22.23.5 · PostgreSQL 16.15 (Ubuntu) |
| INT-009 | D6 · P0 · M | ⛔ | Sem acesso ao banco na nuvem (credencial só no servidor). |
| INT-010 | D1 · P0 · M | ❌ | Campos da API: ['date', 'description', 'event_type', 'id', 'location', 'origin', 'registration_link', 'status', 'time', 'title']. Front lê (event.X): ['date', 'description', 'endDate', 'endTime', 'end_date', 'end_time', 'event_type', 'id', 'is_expired', 'location', 'registration_link', 'status', 'time', 'title', 'type']. Campos do /events/admin: ['is_expired'] (is_expired só existe no admin, ok). Lidos e ausentes em… |
| INT-011 | D1 · P0 · M | ✅ | 4 eventos criados pelo painel; tags corretas na Home=True; cada chip mostra o seu evento={'Palestra': True, 'Workshop': True, 'Hackathon': True, 'Outros': True}. DECISÃO H7: chip 'Minicurso' existe no front, mas o tipo não existe no banco/painel (POST event_type=Minicurso → 422); chip mostra 0 evento(s). Não há tipo Minicurso em lugar nenhum; sugerido remover o chip ou criar o tipo. |
| INT-012 | D1 · P0 · M | ✅ | API: 00:00:00 / 09:05:00; tela: 00:00 / 09:05 |
| INT-013 | D1 · P0 · M | ✅ | Detalhes mostra 'Link de inscrição não informado', sem quebrar |
| INT-014 | D1 · P1 · M | ❌ | Evento 7/09:00 → 8/18:00 no banco; DTSTART=20261129T120000Z DTEND=20261129T130000Z (esperado 20261130T210000Z). A API não devolve campos de fim (nenhum), então o .ics cai na duração padrão de 60 min. Evento de vários dias sai com 1 h no calendário. |
| INT-015 | D1 · P0 · M | ✅ | 422 do servidor usa os ids do formulário ['event_type', 'registration_link']; link 'abc' → campo registration_link marcado (msg: 'Input should be a valid URL, relative URL without a base'); data passada → campo date com 'A data do evento não pode estar no passado.' |
| INT-016 | D1 · P0 · M | ❌ | API=[401, 403]; front: {'401 token inválido': ('/admin/events', True), '403 aluno (não admin)': ('/admin/events', True)}. 401/403 numa ação protegida NÃO volta ao login: a tela do painel fica com erro genérico (o front só tem tratamento de erro, sem logout automático). |
| INT-017 | D1 · P0 · M | ✅ | GET /events devolve {items,page,total_pages}={'items': 'list', 'page': 'int', 'total_pages': 'int'}; Home lê data.items (OK). Limite: a Home pede só page_size=100 (1ª página) — ver INT-020/027. |
| INT-018 | D1 · P0 · M | ⛔ | API aceita X-User-Id e responde 200 {'event_id': 32, 'is_favorited': True}; sem o cabeçalho → 422. Pela interface NÃO dá para favoritar: o componente FavoriteButton existe mas não é renderizado em nenhuma tela (Home/Detalhes sem ★). Contrato testado só na API. |
| INT-019 | D1 · P1 · M | ❌ | Mensagens da API chegam em inglês: ['Not authenticated', 'Evento não encontrado', 'Field required'] (401 sem token, 404 e 422 de campos). O front não traduz o 'msg' do 422 — o aluno/admin pode ver 'Field required'/'Input should be…' no campo. |
| INT-020 | 3.6 · P0 · M | ✅ | 'EXIBINDO 1–20 DE 45 EVENTOS'; 3 páginas; 45 títulos únicos alcançados (todos). Obs.: a Home só busca page_size=100 → ver INT-027 |
| INT-021 | 3.3 · P0 · M | ✅ | Termo só do evento 33 (página 2 da API): encontrado, e sem acento/maiúscula |
| INT-022 | 3.2 · P0 · M | ✅ | Filtro Workshop mostra 12 de 12 Workshops do banco (espalhados pelas 3 páginas) |
| INT-023 | 3.1 · P0 · M | ✅ | Ordem (data, hora, id) idêntica no banco, na API e na tela, inclusive com 4 eventos empatados |
| INT-024 | 2.1 · P0 · M | ✅ | Evento aparece na Home após recarregar, na posição 15 (igual à ordem cronológica do banco) |
| INT-025 | 2.2 · P0 · M | ✅ | Edição de título, data e tipo: banco=('E2E editado', datetime.date(2026, 12, 1), 'Hackathon'); Home e Detalhes mostram o novo; .ics com SUMMARY e data novos |
| INT-026 | 2.3 · P0 · M | ✅ | Excluído pelo painel: some do banco e da Home; o link antigo mostra 'Evento não encontrado' |
| INT-027 | 3.6 · P1 · M | ❌ | 500 eventos no banco, mas a Home mostra 'EXIBINDO 1–20 DE 100 EVENTOS' (0.1s de carga): só os 100 primeiros chegam à tela, porque a Home pede page_size=100 e não percorre as demais páginas da API. Busca por 'Evento 450' (existe no banco) → 0 resultado(s). Eventos além do 100º ficam invisíveis ao aluno (H8/P7 confirmado). |
| INT-028 | 2.2 · P1 · M | ✅ | Outra aba continua com o dado antigo até o F5 e mostra o novo depois, sem erro |
| INT-029 | D1 · P0 · M | ✅ | Título idêntico no banco, API, Home, Detalhes e .ics (escapado conforme iCalendar); <b> exibido como texto, não interpretado |
| INT-030 | 6.1 · P0 · M | ⛔ | API: usuário 1 existe no seed (Pedro Henrique Albuquerque Costa de Medeiros); POST favorite → 200 {'event_id': 24, 'is_favorited': True}; linha em favorito=1. Usuário inexistente (9999) → 404 {'detail': 'Usuário não encontrado'} (erro tratado, sem 500). UI: ⛔ não há botão ★ na Home/Detalhes (FavoriteButton não é usado em nenhuma tela), então o caso 'pela interface' não é executável. |
| INT-031 | 6.1 · P0 · M | ⛔ | API: depois de favoritar, GET /events/favorites devolve 3 evento(s) incluindo 'FAV A'=True (persistido). UI: ⛔ página 'Meus Favoritos' é placeholder fixo ('Você ainda não tem eventos favoritos'), não chama a API. |
| INT-032 | 6.1 · P0 · M | ✅ | DELETE do admin → 204; some de /events/favorites; favorito apagado em cascata; sem 500 |
| INT-033 | 6.1 · P1 · M | ✅ | Evento favoritado vencido: já some de /favorites antes da limpeza (filtro de expirados=True) e a limpeza (200 {'executed_at': '2026-11-22T12:13:10.053991-03:00', 'reference_date': '2026-11-22', 'expired_count': 1, 'deleted_event_ids': [27], 'deleted_titles': ['FAV D (vai expirar)'], 'message': 'Limpeza concluída com sucesso: 1 evento(s) expirado(s) removido(s).'}) apaga a linha de favorito |
| INT-034 | 6.2 · P0 · M | ⛔ | API: DELETE favorite idempotente (→ 200 {'event_id': 24, 'is_favorited': False}); lista vazia devolve []. UI: ⛔ sem tela de favoritos funcional; estado vazio com a frase do Gherkin existe apenas como texto fixo. |
| INT-035 | 6.2 · P0 · M | ✅ | API devolve em ordem cronológica (data, hora): ['FAV B', 'FAV C', 'FAV A']. (A tela de favoritos não consome a API.) |
| INT-036 | 6.1 · P1 · M | ➖ | Limitação do MVP confirmada na API: o 'usuário' do favorito é o cabeçalho X-User-Id (fixo 1 no front); dois clientes com o mesmo cabeçalho compartilham a lista (1=1), e outro id vê lista diferente (3). Registrada como limitação (BE-076); o front tem um 'id anônimo' (localStorage) que NÃO é enviado à API. |
| INT-037 | 6.1 · P2 · M | ➖ | DECISÃO: com 50+ favoritos /events/favorites devolve 51 itens de uma vez, sem paginação (JSON ~11 KB). Aceitável no MVP; sem tela para avaliar a usabilidade. |
| INT-038 | 6.1 · P1 · M | ✅ | 10 POSTs simultâneos no mesmo favorito: todos {200}, 1 única linha no banco (idempotente, sem 500). Cliques rápidos pela UI: ⛔ (sem botão). |
| INT-040 | 4.1 · P0 · M | ❌ | F01 → card na Home com data, hora, local, tipo e origem corretos;  banco: ('Palestra de IA Generativa', datetime.date(2026, 12, 22), datetime.time(19, 0), 'Auditório do CIn', 'Palestra', 'email'); origem email; log 'processado'; ciclo 0.0s DEFEITO: a descrição do card sai 'Palestra de IA Generativa Prezados,' (título + saudação). O parser monta a descrição como o 1º parágrafo de 'título\nencorpo', então qualquer e-ma… |
| INT-041 | 4.2 · P0 · M | ✅ | F02 (texto livre, sem data numérica) → parser insuficiente → IA simulada (J1) → card na Home; log 'processado_ia' |
| INT-042 | 4.1 · P0 · M | ✅ | F05 (sem hora) e F08 (não é evento): nenhum card; log 'ignorado' x2; /extraction/status counts={'processado': 2, 'ignorado': 2}, resumo do ciclo ignored=2. Painel de tela: ⛔ placeholder (contadores verificados pela API). |
| INT-043 | 4.4 · P0 · M | ✅ | F14 (2025): pelo parser → log 'extracao_incompleta' (descartado pela validação: data_no_passado); pela IA → 'extracao_incompleta'; nenhum card na Home |
| INT-044 | 4.4 · P0 · M | ✅ | IA sem data (e J3 sem título, J4 data passada) → nenhum card; 'extracao_incompleta' e presentes em GET /extraction/alerts (5 alertas). Painel 'Extração Incompleta' na tela: ⛔ placeholder (US 4.3 do front não implementada). |
| INT-045 | 4.5 · P0 · M | ❌ | F01 ('Palestra de IA Generativa') + F12 ('Lembrete: Palestra de IA Generativa', mesma data, hora e local) geraram 2 cards: o lembrete foi publicado como outro evento ('Lembrete: Palestra de IA Generativa'). A desduplicação por conteúdo (US 4.5, IESI-76/77) não está na develop; só existe a duplicata por message_id (INT-054). A branch feature/us-4.5-verificar-duplicacao ainda não foi mergeada. (Correção: na 1ª rodada e… |
| INT-046 | 4.6 · P1 · M | ❌ | 1º ciclo (Gemini 500 simulado): {'fetched': 1, 'processed': 0, 'processed_ia': 0, 'ignored': 0, 'unprocessed': 0, 'discarded': 0, 'errors': 1, 'duplicates': 0, 'message': ''} log=('erro', None, '500 Internal Server Error (simulado)'). 2º ciclo (Gemini OK): {'fetched': 1, 'processed': 0, 'processed_ia': 0, 'ignored': 0, 'unprocessed': 0, 'discarded': 0, 'errors': 0, 'duplicates': 1, 'message': ''} (duplicates=1), even… |
| INT-047 | 4.3 · P1 · M | ✅ | Gmail fora: ciclo devolve 'falha ao buscar e-mails: Gmail simulado: 503 Service Unavailable', API sem 500, status last_run_failed=True/last_error='Gmail simulado: 503 Service Unavailable'; Gmail volta: e-mail processado e last_run_failed=False |
| INT-048 | D8 · P0 · M | ✅ | Log/API: remetente vira só domínio e CPF/e-mail/telefone mascarados (nenhum padrão encontrado). Descrição publicada do evento: 'Workshop de Git Prezados alunos,' |
| INT-049 | 4.4 · P1 · M | ✅ | Edição do admin preservada; reprocessar o mesmo e-mail não recria nem sobrescreve; origem continua 'email' |
| INT-050 | 2.3 · P0 · M | ✅ | Evento excluído pelo admin: log mantido com event_id NULL ([('processado', None)]) e o próximo ciclo NÃO recria o evento (0 eventos) |
| INT-051 | 4.1 · P0 · M | ✅ | EXTRACTION_INTERVAL_MINUTES=1: e-mail novo virou card em 58s, sem ação manual |
| INT-052 | 4.1 · P1 · M | ✅ | Lote misto de 50 e-mails em 0.2s: processed=20, processed_ia=5, ignored=15, discarded=10 = resumo ⇄ /status {'processado': 20, 'processado_ia': 5, 'extracao_incompleta': 10, 'ignorado': 15} ⇄ banco (25 eventos, 50 logs). Sem erros. |
| INT-053 | 4.1 · P1 · M | ✅ | E-mail só-HTML: tags/script/style removidos; local 'Sala E112 & Anexo'; descrição 'Workshop de HTML Limpo Prezados, Workshop de HTML Limpo Data: 22/12/2026 Hora: 1' |
| INT-054 | 4.1 · P0 · M | ✅ | 2º ciclo com os mesmos 4 e-mails: duplicates=4, nenhum card novo (2 cards de e-mail) |
| INT-055 | 4.6 · P1 · M | ✅ | PostgreSQL derrubado durante o ciclo: a API respondeu 500 (Internal Server Error); com o banco de volta, o ciclo seguinte processa o e-mail normalmente (nada ficou registrado pela metade) |
| INT-056 | 4.1 · P0 · M | ✅ | E-mail '19h' → banco 19:00, tela 19:00 e .ics DTSTART=20261222T220000Z (19:00 Recife = 22:00Z) |
| INT-057 | 4.4 · P0 · M | ✅ | Relógio simulado em 23/11 01:00 UTC (= 22/11 22:00 em Recife), executado em processo contra o banco real: e-mail com a data de hoje (22/11, 23h) foi aceito (processed=1), publicado e não é considerado expirado. (Relógio simulado com freezegun, não o relógio do sistema.) |
| INT-058 | 4.1 · P1 · M | ✅ | Acentos, & e emoji idênticos no e-mail, banco, Detalhes e .ics |
| INT-059 | 4.1 · P1 · M | ✅ | Do e-mail na caixa simulada até o card: 58s (limite = 1 intervalo de 60 s + 5 s). Cronometrado após o job já estar rodando. |
| INT-060 | 5.1 · P0 · M | ✅ | Evento de 01/09 com referência 02/09: relatório {'executed_at': '2026-11-22T17:14:43.243760-03:00', 'reference_date': '2026-09-02', 'expired_count': 1, 'deleted_event_ids': [1], 'deleted_titles': ['LIMPA 0901'], 'message': 'Limpeza concluída com sucesso: 1 evento(s) expirado(s) removido(s).'}; some da Home, dos favoritos e do banco; log 'LOG60' mantido com event_id NULL |
| INT-061 | 5.1 · P0 · M | ✅ | Evento de 01/10 com referência 05/09: expired_count=0 e a linha continua no banco. (Obs.: como hoje já é 22/11, a Home real esconde esse evento por ser passado; o caso foi avaliado pela limpeza, não pela tela.) |
| INT-062 | 5.2 · P0 · M | ✅ | CLEANUP_INTERVAL_MINUTES=1: evento expirado inserido direto no banco sumiu em 58s, sem ação manual |
| INT-063 | 5.2 · P0 · M | ✅ | POST /events/cleanup: expired_count=7 = linhas realmente apagadas (10→3); relatório: {'executed_at': '2026-11-22T17:14:45.530205-03:00', 'reference_date': '2026-11-22', 'expired_count': 7, 'deleted_event_ids': [1, 2, 3, 4, 5, 6, 7], 'deleted_titles': ['EXP 0', 'EXP 1', 'EXP 2', 'EXP 3', 'EXP 4', 'EXP 5', 'EXP 6'], 'message': 'Limpeza concluída com sucesso: 7 evento(s) expirado(s) removido(s).'} |
| INT-064 | 5.1 · P0 · M | ✅ | Hoje e multi-dia em andamento permanecem; ontem e multi-dia encerrado ontem são removidos (expired_count=2) |
| INT-065 | 5.1 · P0 · M | ✅ | Relógio simulado: às 23:59 de Recife (02:59Z de 23/11) a limpeza apaga 0 e o evento de 22/11 permanece; às 00:01 de Recife (03:01Z) apaga 1 e some. Nunca antes da meia-noite de Recife. |
| INT-066 | 5.2 · P1 · M | ✅ | 40 leituras da Home em paralelo com 3 limpezas simultâneas: nenhum erro (códigos 200); estado final 5 eventos válidos |
| INT-067 | 4.4 · P1 · M | ✅ | Lembrete com data passada após a limpeza: descartado pela validação (discarded=1), não recriado |
| INT-068 | D8 · P1 · M | ✅ | Logs de eventos limpos: event_id NULL (visto em INT-060/050) e nenhum dado pessoal ([('cin.ufpe.br', 'extracao_incompleta', None, '{"title": "Lembrete: Palestra X", "date": "2026-11-19", "time": "19:00:00", "location": "Auditório do CIn", "description": "Lembrete: Palestra X Prezados alunos,", "event_type": "Palestra", "registration_link": "https://cin.ufpe.br/inscricao/ia", "missing": []}', 'evento descartado pela v… |
| INT-069 | 5.2 · P1 · M | ✅ | 1000 expirados com 1000 favoritos e 1000 logs vinculados: limpeza concluiu em 0.7s (expired_count=1000); favoritos apagados em cascata, logs com event_id NULL; Home responde com os 5 vivos |
| INT-070 | 1.1 · P0 · M | ⛔ | Passos pela interface: {'login': True, 'criar': True, 'editar': True, 'excluir': True, 'extração/painel (tela)': False, 'sair': True}. Login, criar, editar, excluir e sair funcionam e persistem no banco; os passos 'executar extração' e 'ver painel' NÃO existem na tela (a página Extração é um placeholder 'será implementado na US 4.3'; a extração só roda pela API/agendador). |
| INT-071 | 1.1 · P0 · M | ❌ | Token de 1 min expirado com o formulário 'Novo evento' preenchido: ao salvar, a tela mostra 'Token inválido ou expirado' e MANTÉM os dados digitados (nada se perde em silêncio; banco 23→23, evento não gravado). Defeito: não há redirecionamento ao /login nem botão de nova autenticação; ao abrir a lista de eventos aparece só 'Não foi possível carregar os eventos. Tentar novamente' (erro genérico, a causa é a sessão exp… |
| INT-072 | 1.2 · P1 · M | ➖ | Depois de 'Sair' o token copiado ainda funciona na API (GET /events/admin → 200) até expirar: não há revogação/lista de bloqueio (BE-015). Risco conhecido do JWT stateless; expira em JWT_EXPIRE_MINUTES (60 por padrão). Decisão do time: aceitar e registrar. |
| INT-073 | D7 · P0 · M | ✅ | Sem login: as 4 rotas do painel vão para /login; a API recusa tudo ({'/events/admin': 403, '/events/cleanup': 403, '/extraction/run': 403, '/extraction/status': 403, '/extraction/alerts': 403, 'POST /events': 403, 'DELETE /events/1': 403, 'PUT /events/1': 403}) |
| INT-074 | D7 · P0 · M | ✅ | Token falso: o painel abre (a rota só confere se existe token), mas a lista não carrega ('Não foi possível…') e criar evento é recusado (banco 23→23); nada protegido foi lido nem alterado |
| INT-075 | 1.1 · P0 · M | ✅ | Admin do seed (admin@cin.ufpe.br) entra no painel; usuário comum (is_admin=false) com senha correta é recusado: API 403 {'detail': 'Acesso restrito a administradores'}; na tela fica em /login sem token |
| INT-076 | D6 · P1 · M | ➖ | CORS: origem de outro computador (http://192.168.0.50:5173) → access-control-allow-origin=* e preflight 200 (allow_origins=['*']). Não testei de outra máquina de verdade. Atenção: o front é compilado com VITE_API_URL; se ficar 'localhost', o navegador do outro computador chamará o PRÓPRIO localhost e falhará — é preciso usar o IP/host do servidor. |
| INT-077 | D7 · P0 · M | ✅ | Matriz confirmada na API (anônimo / admin): Ver lista: 200/200; Ver detalhes: 200/200; Favoritar: 200/200; Criar: 403/201; Editar: 403/200; Listar admin: 403/200; Executar limpeza: 403/200; Executar extração: 403/200; Ver status/alertas: 403/200; Excluir: 403/204 |
| INT-078 | 2.2 · P1 · M | ✅ | Dois admins editando o mesmo evento: ambos 200; vale a última gravação ('Versão do admin 2'), sem erro nem aviso de conflito (sem controle de versão, por decisão do MVP) |
| INT-079 | 1.1 · P1 · M | ✅ | Senha 'Sênha#çã@2026!' (acentos e símbolos): login pela interface funciona |
| NF-001 | D6 · P1 · A | ✅ | 50 usuários simultâneos por 30 s (versão curta do caso, que pede 2 min) em Home+Detalhes: 13192 requisições, 0% de 5xx, p95=194 ms, mediana=110 ms. API local com 1 processo, sem rede. |
| NF-002 | D6 · P1 · A | ✅ | Ciclo de 50 e-mails (processed=50) enquanto 20 usuários navegam: 605 requisições, 0 erros, p95=155 ms |
| NF-003 | D6 · P1 · A | ✅ | 10 000 eventos, 1 000 usuários, 50000 favoritos: GET /events?page_size=100 9 ms; página 50 (20 itens) 10 ms; /events/favorites de um usuário (50 itens) 8 ms; /events/admin (sem paginação, 1 itens, 0 KB) 1 ms; Home no navegador 0.3 s mostrando 'EXIBINDO 1–20 DE 100 EVENTOS'. Limites: a Home só enxerga 100 dos 10 000 (INT-027) e /events/admin devolve tudo de uma vez. |
| NF-004 | D6 · P0 · M | ✅ | PostgreSQL derrubado com a Home aberta: erro tratado ('Não foi possível carregar os eventos' + 'Tentar novamente'); com o banco de volta, o botão recarrega os 20 eventos, sem reiniciar a API nem o front |
| NF-005 | D6 · P1 · M | ✅ | pg_dump com a API no ar → apagados todos os eventos (Home vazia) → restauração com psql → a API lista os mesmos 23 eventos, na mesma ordem, sem reiniciar |
| NF-006 | D7 · P1 · A | ⛔ | OWASP ZAP não instalado no ambiente. |
| NF-007 | D8 · P0 · M | ⛔ | Consolidação parcial: ver INT-048/048b/048c, NF-013 e o registro BD/BE; falta o FE-118 por humano. |
| NF-008 | D6 · P0 · A | ✅ | Matriz 3 servidores (UTC, Recife, Nova York) × 4 horários (00:30, 12:00, 21:30, 23:50) = 12 células, relógio simulado em processo: em TODAS a validação aceita a data de hoje e descarta a de ontem, e a expiração marca hoje=não expirado/ontem=expirado, sempre pelo dia de Recife (independe do fuso do servidor). O `.ics` ficou idêntico com o navegador em UTC, Recife e Nova York (ver NF-009). Observação: a 'data de hoje'… |
| NF-009 | D6 · P1 · A | ✅ | 29/02/2028, 31/12 às 23:30 e 00:00 criados (201) e listados; .ics idêntico com o navegador em UTC, Recife e Nova York (29/02/2028 → DTSTART 20280229T130000Z; 31/12 23:30 → 20270101T023000Z, já em 01/01 UTC). Evento que termina hoje às 02:00 permanece; o que terminou ontem é removido pela limpeza. |
| NF-010 | D1 · P1 · M | ⛔ | Exige pessoa com teclado e leitor de tela. |
| NF-011 | D6 · P1 · M | ⛔ | Exige dispositivos reais. |
| NF-012 | D1 · P1 · M | ⛔ | Exige pessoa/dispositivo. |
| NF-013 | D6 · P1 · M | ✅ | message_id → event_id por JOIN: ('TR1', 'cin.ufpe.br', 'processado', 1); remetente só como domínio |
| NF-014 | D6 · P0 · M | ⛔ | Exige clone limpo em outra máquina. |
| NF-015 | D7 · P0 · M | ✅ | Hosts contatados durante o fluxo (dev + preview): ['127.0.0.1:4173', 'localhost:5173', 'localhost:8000'] (só o front e a API). `dist/` sem chave, sem URL de banco/Gmail/Gemini. Obs.: o bundle ainda embute dados de mock (https://example.com…), sem impacto de segurança. |
| INT-080 | 4.2 · P0 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-081 | 4.1 · P0 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-082 | 4.2 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-083 | 4.1 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-084 | D8 · P0 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-085 | 4.1 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-086 | 4.2 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-087 | 4.2 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-088 | 4.1 · P1 · M | ⛔ | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-089 | 4.2 · P2 · M | ✅ | Num ciclo de 50 e-mails (20 estruturados válidos, 10 avisos, 10 de data passada, 5 texto livre, 5 sem hora) o app fez 20 chamada(s) à IA. Com ciclo a cada 12 h (2 ciclos/dia, EXTRACTION_INTERVAL_MINUTES=720) são ~40 chamadas/dia no pior caso deste lote (e no máximo 2×50=100 se nenhum e-mail passar pelo parser), contra o limite de 1 024/dia do modelo gratuito do OpenRouter citado na reunião. Dentro da cota. |
| INT-090 | D6 · P0 · M | ⛔ | Item de processo: só após as correções. |
| INT-091 | D1 · P0 · M | ⛔ | Item de processo (humano). |
| INT-092 | D1 · P0 · M | ⛔ | Item de processo (humano). |
| INT-093 | D9 · P0 · M | ⛔ | Item de processo (humano). |
| INT-094 | D4 · P0 · M | ⛔ | Item de processo (humano). |
| INT-095 | D6 · P1 · M | ❌ | git ls-files na develop: nomes duplicados por maiúscula/minúscula=[['backend/app/core/Security.py', 'backend/app/core/security.py']]; lixo versionado=nenhum; segredos=nenhum; 5 branches remotas ainda existem (develop, feat/Dockerização-Deploy, feature/Integração-DB-Backend-extracao, feature/us-4.5-verificar-duplicacao, main). |
| INT-096 | D9 · P1 · M | ❌ | README.md tem 0 bytes (vazio): não há setup do zero. docs/ contém: ['backlog', 'db', 'dev_notes', 'diagramas', 'entregas', 'sprint_burndowns']. O setup real só está em docs/db/migracao-postgresql.md e docs/dev_notes. Diagrama C4 (IESI-63): não encontrado em docs/. |
| INT-097 | D9 · P1 · M | ⛔ | Item de processo (Jira) — sem alterar o Jira por regra. |
| INT-098 | D9 · P1 · M | ⛔ | Item de processo (humano). |

## 5. Casos extras (não estavam no roteiro)

- **INT-048b** ✅ — Com o e-mail de exemplo (saudação 'Prezados,' no 1º parágrafo) a descrição publicada não tem dado pessoal, mas por acaso: ver INT-040 (descrição = 'título + saudação') e INT-048c.
- **INT-048c** ✅ — Descrição pública sem dados pessoais no teste (e-mail com contato no 2º parágrafo): a descrição só leva o 1º parágrafo, então o telefone/e-mail não apareceu. Proteção só por acaso — o parser publica 'título + primeiras linhas' (ver INT-040); se o contato estiver no 1º parágrafo livre, ele iria para o card.
- **INT-052b** ❌ — Havia 60 e-mails na janela, o ciclo leu 50 (GMAIL_MAX_RESULTS=50, sem paginação nem fila): os 10 mais antigos NUNCA serão lidos, nem no ciclo seguinte (fetched=50). Em volume real (>50 e-mails/12 h) eventos se perdem.

## 6. Não executado e motivo

| ID | Motivo |
|---|---|
| INT-007 | Sem daemon Docker no ambiente; PR do Albert (IESI-85) ainda aberto. Refazer INT-001..005 contra os contêineres após o merge. |
| INT-009 | Sem acesso ao banco na nuvem (credencial só no servidor). |
| NF-006 | OWASP ZAP não instalado no ambiente. |
| NF-007 | Consolidação parcial: ver INT-048/048b/048c, NF-013 e o registro BD/BE; falta o FE-118 por humano. |
| NF-010 | Exige pessoa com teclado e leitor de tela. |
| NF-011 | Exige dispositivos reais. |
| NF-012 | Exige pessoa/dispositivo. |
| NF-014 | Exige clone limpo em outra máquina. |
| INT-080 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-081 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-082 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-083 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-084 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-085 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-086 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-087 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-088 | Exige Gmail/Gemini reais e/ou corpus de e-mails reais anonimizados (sem chaves, por regra). |
| INT-090 | Item de processo: só após as correções. |
| INT-091 | Item de processo (humano). |
| INT-092 | Item de processo (humano). |
| INT-093 | Item de processo (humano). |
| INT-094 | Item de processo (humano). |
| INT-097 | Item de processo (Jira) — sem alterar o Jira por regra. |
| INT-098 | Item de processo (humano). |

## 7. Próximos passos sugeridos

- Reexecutar os ❌ depois das correções (os scripts estão prontos e repetem em poucos minutos).
- Quando o PR do Albert entrar: INT-007 e repetir INT-001..005 nos contêineres.
- Os itens ⛔ de Gmail/Gemini reais (INT-080..088) precisam de uma sessão com as chaves e o corpus anonimizado.
