# Registro dos testes já executados — cin-event-hub

**Data da execução:** 22/11/2026 · **Código testado:** `origin/develop` @ `c131e9d` (merge do PR #31, fuso Recife) · **Ambiente:** sandbox Linux, PostgreSQL 16, Python 3.13, Node 22 · **Commits/alterações no repo:** nenhum (só leitura)

## 1. Resumo

| Camada | Como rodar | Resultado | Obs. |
|---|---|---|---|
| Banco (PostgreSQL) | `python database/run_tests.py` | ✅ **106 verificações ok** (schema 58 + seed eventos 18 + seeds de usuários, extrações e favoritos 30) | cria e apaga bancos temporários `iesi_test_*` |
| Backend (pytest, PostgreSQL) | `cd backend && python -m pytest -v` | ✅ **291 passed, 0 failed** (com `google-genai` instalado) | com o `requirements.txt` atual a instalação **falha** (ver 5.1); sem `google-genai`: 289 passed + 2 skipped |
| Frontend (node:test) | `cd frontend && npm test` | ✅ **9 passed, 0 failed** | `Favoritebutton.test.jsx` existe mas **não roda** no `npm test` (ver 5.2) |

**Total automatizado: 106 + 291 + 9 = 406 verificações, nenhuma falha.**

### Histórico (execuções anteriores, das tasks que fizemos)

| Quando | O que | Resultado |
|---|---|---|
| IESI-60 (LGPD) | `test_minimizacao_lgpd.py` | 32 passed, 1 skipped (SQLite); 33 passed em PostgreSQL |
| IESI-60 | suíte completa, SQLite | 111 passed, 1 skipped |
| IESI-60 | suíte completa, PostgreSQL | 144 passed |
| IESI-60 | testes novos sem a mudança em `extraction_service.py` | 6 falham (prova de que os testes pegam o bug) |
| Hoje | develop `c131e9d`, tudo | números da seção 1 |

## 2. Banco de dados — `database/run_tests.py`

Saída real da execução (cada linha é uma verificação SQL em `database/tests/*.sql`):

```text
Schema (IESI-56)
    > aplicar o schema
    > testar restrições e relacionamentos
        ok  usuário aluno válido
        ok  valores padrão do usuário: não é admin e data de cadastro é hoje (Recife UTC-3)
        ok  virada do dia em Recife (UTC-3) ocorre às 03:00 UTC
        ok  e-mail de usuário repetido
        ok  nome só com espaços
        ok  e-mail vazio
        ok  senha_hash vazia
        ok  nome_perfil vazio
        ok  usuário sem nome_perfil (NOT NULL)
        ok  extração ignorada, sem evento e sem dados extraídos
        ok  created_at da extração é preenchido e event_id fica nulo
        ok  os seis status de extração são aceitos
        ok  remetente vazio é aceito (o Gmail pode não mandar o From)
        ok  status de extração inválido
        ok  gmail_message_id vazio
        ok  mesma mensagem do Gmail registrada duas vezes
        ok  extração sem status (NOT NULL)
        ok  extração sem remetente (NOT NULL)
        ok  evento manual válido, cadastrado por um admin
        ok  valores padrão do evento: status active, origin manual e datas de criação preenchidas
        ok  mesmo título em outra data
        ok  evento com fim no dia seguinte e capacidade
        ok  evento vindo de e-mail
        ok  os quatro tipos de evento são aceitos
        ok  evento de e-mail sem link (o parser pode não achar um — US 4.1)
        ok  status inactive é aceito
        ok  título só com espaços
        ok  descrição vazia
        ok  local só com espaços
        ok  link de inscrição sem http(s)
        ok  evento manual sem link de inscrição (vazio)
        ok  evento de e-mail com link preenchido sem http(s)
        ok  tipo de evento inválido
        ok  status do evento inválido
        ok  capacidade zero
        ok  fim antes do início
        ok  end_event_date sem end_event_time
        ok  admin (usuário) inexistente
        ok  evento sem data
        ok  evento sem hora
        ok  evento sem local
        ok  evento sem link de inscrição
        ok  extração processada ligada ao evento que gerou
        ok  extração ligada a evento inexistente
        ok  extração ignorada não pode apontar para evento
        ok  extração processada pela IA ligada ao evento que gerou
        ok  extração incompleta não pode apontar para evento
        ok  extração não processada não pode apontar para evento
        ok  extração processada sem evento (evento já apagado)
        ok  aluno favorita um evento
        ok  favoritar o mesmo evento duas vezes
        ok  favorito de usuário inexistente
        ok  favorito de evento inexistente
        ok  apagar o evento apaga os favoritos dele
        ok  apagar o aluno apaga os favoritos dele e mantém o evento favoritado
        ok  apagar o admin mantém o evento, com admin_id nulo
        ok  apagar o evento mantém o log de extração, com event_id nulo
        ok  apagar a extração mantém o evento gerado por ela
  PASSOU

Seed (IESI-57)
    > aplicar o schema
    > aplicar o seed
    > testar o seed
        ok  20 eventos no total
        ok  6 palestras, 8 workshops, 4 hackathons e 2 do tipo Outro
        ok  nenhum evento no passado (a limpeza da US 5.1 não os apaga)
        ok  um evento hoje
        ok  um dia com 3 eventos (teste de ordenação por hora)
        ok  título longo (150+) e descrição longa (400+ caracteres)
        ok  há evento que termina em outro dia e evento sem horário de fim
        ok  há eventos com e sem capacidade
        ok  todos os eventos são ativos, manuais e sem admin
    > rodar o seed de novo
    > testar de novo (nada pode duplicar)
        ok  20 eventos no total
        ok  6 palestras, 8 workshops, 4 hackathons e 2 do tipo Outro
        ok  nenhum evento no passado (a limpeza da US 5.1 não os apaga)
        ok  um evento hoje
        ok  um dia com 3 eventos (teste de ordenação por hora)
        ok  título longo (150+) e descrição longa (400+ caracteres)
        ok  há evento que termina em outro dia e evento sem horário de fim
        ok  há eventos com e sem capacidade
        ok  todos os eventos são ativos, manuais e sem admin
  PASSOU

Seeds de usuários, extrações e favoritos
    > aplicar o schema
    > aplicar o seed de eventos
    > aplicar o seed de usuários
    > aplicar o seed de extrações
    > aplicar o seed de favoritos
    > testar os seeds
        ok  5 usuários: 2 administradores e 3 comuns
        ok  todos os e-mails dos usuários são de example.com
        ok  datas de cadastro nos últimos 90 dias e nunca no futuro
        ok  há nome com acento e nome com mais de 40 caracteres
        ok  7 extrações seed, e os 6 status do CHECK aparecem
        ok  2 processado, 1 processado_ia e 1 de cada um dos outros status
        ok  só processado e processado_ia têm event_id, e o evento é de origem email
        ok  3 eventos de e-mail, ativos e no futuro, um deles sem link de inscrição
        ok  o seed de eventos manuais continua com 20 eventos
        ok  source_email só guarda domínio (sem endereço de pessoa)
        ok  extracted_data é objeto JSON quando preenchido; erro e ignorado têm mensagem
        ok  datas de criação das extrações nunca estão no futuro
        ok  8 favoritos, todos de usuários e eventos que existem
        ok  Marina tem 3 favoritos, Pedro e Júlia 2, Ana 1 e Carlos nenhum
        ok  um evento favoritado por 2 usuários e favoritos em eventos de e-mail
    > rodar o seed de usuários de novo
    > rodar o seed de extrações de novo
    > rodar o seed de favoritos de novo
    > testar de novo (nada pode duplicar)
        ok  5 usuários: 2 administradores e 3 comuns
        ok  todos os e-mails dos usuários são de example.com
        ok  datas de cadastro nos últimos 90 dias e nunca no futuro
        ok  há nome com acento e nome com mais de 40 caracteres
        ok  7 extrações seed, e os 6 status do CHECK aparecem
        ok  2 processado, 1 processado_ia e 1 de cada um dos outros status
        ok  só processado e processado_ia têm event_id, e o evento é de origem email
        ok  3 eventos de e-mail, ativos e no futuro, um deles sem link de inscrição
        ok  o seed de eventos manuais continua com 20 eventos
        ok  source_email só guarda domínio (sem endereço de pessoa)
        ok  extracted_data é objeto JSON quando preenchido; erro e ignorado têm mensagem
        ok  datas de criação das extrações nunca estão no futuro
        ok  8 favoritos, todos de usuários e eventos que existem
        ok  Marina tem 3 favoritos, Pedro e Júlia 2, Ana 1 e Carlos nenhum
        ok  um evento favoritado por 2 usuários e favoritos em eventos de e-mail
  PASSOU

Resultado: TUDO PASSOU (106 verificações ok)
```

## 3. Backend — pytest

Saída real do `pytest -v`, agrupada por arquivo. Descrição = docstring do teste (quando existe).

| Arquivo | Qtde | Resultado |
|---|---|---|
| `tests/api/test_list_events.py` | 13 | ✅ todos passaram |
| `tests/api/test_rotas_integracao.py` | 32 | ✅ todos passaram |
| `tests/repositories/test_event_repository.py` | 8 | ✅ todos passaram |
| `tests/services/favorites/test_service.py` | 5 | ✅ todos passaram |
| `tests/services/test_event_service.py` | 10 | ✅ todos passaram |
| `tests/test_admin_events.py` | 4 | ✅ todos passaram |
| `tests/test_auth_usuario.py` | 14 | ✅ todos passaram |
| `tests/test_cleanup_service.py` | 15 | ✅ todos passaram |
| `tests/test_delete_evento_com_log.py` | 1 | ✅ todos passaram |
| `tests/test_extraction_service.py` | 14 | ✅ todos passaram |
| `tests/test_gemini_client.py` | 13 | ✅ todos passaram |
| `tests/test_metrics.py` | 6 | ✅ todos passaram |
| `tests/test_minimizacao_lgpd.py` | 33 | ✅ todos passaram |
| `tests/test_models_crud.py` | 35 | ✅ todos passaram |
| `tests/test_models_vs_schema.py` | 16 | ✅ todos passaram |
| `tests/test_parser.py` | 7 | ✅ todos passaram |
| `tests/test_parte_b_correcoes.py` | 22 | ✅ todos passaram |
| `tests/test_roteiro_wallyson.py` | 24 | ✅ todos passaram |
| `tests/test_validation_service.py` | 19 | ✅ todos passaram |

### `tests/api/test_list_events.py` — 13 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_sem_parametros_retorna_os_20_primeiros_com_metadados` | ✅ |  |
| `test_pagina_seguinte_traz_os_proximos_eventos` | ✅ |  |
| `test_ultima_pagina_traz_so_o_que_sobrou` | ✅ |  |
| `test_page_size_muda_o_tamanho_e_o_total_de_paginas` | ✅ |  |
| `test_pagina_alem_do_total_devolve_lista_vazia` | ✅ |  |
| `test_sem_eventos_devolve_zero_paginas` | ✅ |  |
| `test_eventos_inativos_nao_entram_no_total` | ✅ |  |
| `test_cada_item_mantem_o_formato_do_evento` | ✅ |  |
| `test_parametros_invalidos_retornam_422[params0]` | ✅ |  |
| `test_parametros_invalidos_retornam_422[params1]` | ✅ |  |
| `test_parametros_invalidos_retornam_422[params2]` | ✅ |  |
| `test_parametros_invalidos_retornam_422[params3]` | ✅ |  |
| `test_parametros_invalidos_retornam_422[params4]` | ✅ |  |

### `tests/api/test_rotas_integracao.py` — 32 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_health` | ✅ |  |
| `test_login_ok_devolve_token` | ✅ |  |
| `test_login_invalido_401[admin@cin.ufpe.br-errada]` | ✅ |  |
| `test_login_invalido_401[outro@cin.ufpe.br-123456]` | ✅ |  |
| `test_login_usa_tabela_usuario` | ✅ |  |
| `test_login_usuario_comum_403` | ✅ |  |
| `test_login_campo_vazio_ou_email_invalido_422` | ✅ |  |
| `test_rotas_de_admin_recusam_sem_token[post-/events]` | ✅ |  |
| `test_rotas_de_admin_recusam_sem_token[put-/events/1]` | ✅ |  |
| `test_rotas_de_admin_recusam_sem_token[delete-/events/1]` | ✅ |  |
| `test_rotas_de_admin_recusam_sem_token[post-/extraction/run]` | ✅ |  |
| `test_token_invalido_401` | ✅ |  |
| `test_criar_evento_grava_na_tabela_events` | ✅ |  |
| `test_criar_evento_invalido_nao_grava[extra0-422]` | ✅ |  |
| `test_criar_evento_invalido_nao_grava[extra1-422]` | ✅ |  |
| `test_criar_evento_invalido_nao_grava[extra2-422]` | ✅ |  |
| `test_criar_evento_invalido_nao_grava[extra3-422]` | ✅ |  |
| `test_criar_evento_invalido_nao_grava[extra4-422]` | ✅ |  |
| `test_buscar_evento_por_id_e_404` | ✅ |  |
| `test_listagem_so_traz_ativos` | ✅ |  |
| `test_editar_evento_atualiza_a_linha` | ✅ |  |
| `test_excluir_evento` | ✅ |  |
| `test_favoritar_e_desfavoritar_grava_na_tabela_favorito` | ✅ |  |
| `test_favoritar_evento_inexistente_404` | ✅ |  |
| `test_favoritar_sem_header_422` | ✅ |  |
| `test_favoritar_com_usuario_inexistente_404` | ✅ |  |
| `test_excluir_evento_remove_favoritos` | ✅ |  |
| `test_extracao_grava_evento_e_log` | ✅ |  |
| `test_extracao_e_idempotente` | ✅ |  |
| `test_extracao_email_sem_dados_vira_ignorado` | ✅ |  |
| `test_extracao_sem_credenciais_nao_quebra` | ✅ |  |
| `test_evento_extraido_aparece_na_listagem_e_excluir_mantem_log` | ✅ |  |

### `tests/repositories/test_event_repository.py` — 8 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_limit_restringe_a_quantidade_de_eventos` | ✅ |  |
| `test_sem_parametros_retorna_os_20_primeiros` | ✅ |  |
| `test_offset_pula_os_eventos_das_paginas_anteriores` | ✅ |  |
| `test_ultima_pagina_retorna_apenas_o_que_sobrou` | ✅ |  |
| `test_offset_alem_do_total_retorna_lista_vazia` | ✅ |  |
| `test_so_eventos_ativos_entram_na_paginacao` | ✅ |  |
| `test_ordem_cronologica_considera_a_hora_no_mesmo_dia` | ✅ |  |
| `test_paginas_nao_repetem_nem_perdem_eventos_empatados` | ✅ |  |

### `tests/services/favorites/test_service.py` — 5 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_favoritar_evento_existente_ainda_nao_favoritado` | ✅ | Dado um evento existente que o usuário ainda não favoritou |
| `test_favoritar_evento_ja_favoritado_e_idempotente` | ✅ | Dado um evento que o usuário já tinha favoritado |
| `test_favoritar_evento_inexistente_levanta_erro` | ✅ | Dado que o evento não existe |
| `test_desfavoritar_evento_favoritado` | ✅ | Dado um evento favoritado pelo usuário |
| `test_desfavoritar_evento_nao_favoritado_e_idempotente` | ✅ | Dado um evento que o usuário não tinha favoritado |

### `tests/services/test_event_service.py` — 10 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_padrao_busca_a_primeira_pagina_de_20` | ✅ |  |
| `test_offset_e_calculado_a_partir_da_pagina` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[0-20-0]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[1-20-1]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[20-20-1]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[21-20-2]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[45-20-3]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[40-20-2]` | ✅ |  |
| `test_total_de_paginas_arredonda_para_cima[7-3-3]` | ✅ |  |
| `test_devolve_os_itens_do_repositorio` | ✅ |  |

### `tests/test_admin_events.py` — 4 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_admin_events_requires_authentication` | ✅ |  |
| `test_admin_events_lists_active_expired_and_inactive` | ✅ |  |
| `test_admin_events_uses_end_date_to_determine_expiration` | ✅ |  |
| `test_admin_events_are_sorted_by_date_and_time` | ✅ |  |

### `tests/test_auth_usuario.py` — 14 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_model_admin_nao_existe_mais` | ✅ |  |
| `test_repositorio_cria_admin_na_tabela_usuario` | ✅ |  |
| `test_get_admin_by_email_ignora_usuario_comum` | ✅ |  |
| `test_login_de_admin_retorna_token` | ✅ |  |
| `test_login_com_credenciais_invalidas[admin@cin.ufpe.br-errada]` | ✅ |  |
| `test_login_com_credenciais_invalidas[ninguem@cin.ufpe.br-senha-forte-123]` | ✅ |  |
| `test_login_de_usuario_comum_e_recusado` | ✅ |  |
| `test_rota_login_admin_200` | ✅ |  |
| `test_rota_login_senha_errada_401` | ✅ |  |
| `test_rota_login_usuario_comum_403` | ✅ |  |
| `test_admin_cria_evento_e_fica_registrado_como_quem_cadastrou` | ✅ |  |
| `test_usuario_comum_nao_acessa_rota_de_admin` | ✅ |  |
| `test_token_de_usuario_removido_perde_acesso` | ✅ |  |
| `test_token_invalido_401` | ✅ |  |

### `tests/test_cleanup_service.py` — 15 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_exclusao_automatica_de_evento_expirado_com_log` | ✅ | Cenário Gherkin: Exclusão automática de evento expirado. |
| `test_evento_com_data_futura_nao_e_excluido` | ✅ | Cenário Gherkin: Evento com data futura não é excluído. |
| `test_evento_no_proprio_dia_nao_e_expirado` | ✅ | Eventos marcados para o próprio dia de referência ainda estão válidos. |
| `test_limpeza_multiplos_eventos_remove_apenas_expirados` | ✅ | Testa cenário com múltiplos eventos mistos no passado e no futuro. |
| `test_is_event_expired_helper` | ✅ | Testa função auxiliar is_event_expired. |
| `test_desvinculacao_segura_com_log_de_extracao` | ✅ | Garante que evento criado por extração de e-mail é apagado desvinculando o log. |
| `test_evento_multidias_que_termina_no_futuro_permanece_visivel` | ✅ | Evento de vários dias que começou no passado mas só termina no futuro não é excluído. |
| `test_evento_multidias_que_terminou_no_passado_e_excluido` | ✅ | Evento de vários dias cujo término já ocorreu é excluído. |
| `test_limpeza_rejeita_data_futura_por_padrao` | ✅ | Passar reference_date no futuro levanta FutureReferenceDateError. |
| `test_execucao_autonoma_do_job_gera_relatorio` | ✅ | Cenário Gherkin: Agendamento de limpeza. |
| `test_start_and_shutdown_cleanup_scheduler` | ✅ | Testa o ciclo de vida do scheduler (inicialização e encerramento). |
| `test_cleanup_scheduler_desativado_nao_inicia` | ✅ | Quando CLEANUP_ENABLED=False, o agendador não deve criar jobs. |
| `test_trigger_cleanup_requer_autenticacao` | ✅ | Tentativa sem JWT deve retornar 401 ou 403. |
| `test_trigger_cleanup_com_sucesso` | ✅ | Admin autenticado pode disparar a limpeza e receber o relatório. |
| `test_trigger_cleanup_rejeita_data_futura` | ✅ | Admin não pode passar data de referência futura (evita apagar o banco acidentalmente). |

### `tests/test_delete_evento_com_log.py` — 1 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_apagar_evento_extraido_de_email_mantem_o_log` | ✅ |  |

### `tests/test_extraction_service.py` — 14 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_email_completo_e_persistido_com_log` | ✅ |  |
| `test_varredura_e_idempotente` | ✅ |  |
| `test_email_sem_dados_e_ignorado_com_log_de_erro` | ✅ |  |
| `test_email_sem_local_e_contado_como_ignorado` | ✅ |  |
| `test_nao_configurado_nao_faz_nada` | ✅ |  |
| `test_falha_na_gmail_api_nao_quebra_o_job` | ✅ |  |
| `test_ia_extrai_email_de_formato_variado_e_publica` | ✅ |  |
| `test_ia_conclui_que_nao_e_evento_e_ignora` | ✅ |  |
| `test_ia_sem_campos_obrigatorios_gera_alerta` | ✅ |  |
| `test_ia_com_falha_operacional_gera_erro` | ✅ |  |
| `test_ia_com_data_no_passado_e_descartada` | ✅ |  |
| `test_ia_com_titulo_vazio_e_descartada` | ✅ |  |
| `test_ia_com_data_de_hoje_e_publicada` | ✅ |  |
| `test_alertas_incluem_descartes_e_registos_legados` | ✅ |  |

### `tests/test_gemini_client.py` — 13 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_is_configured_depende_da_chave` | ✅ |  |
| `test_extrai_evento_valido` | ✅ |  |
| `test_aceita_resposta_entre_cercas_markdown` | ✅ |  |
| `test_aceita_data_brasileira_e_hora_com_h` | ✅ |  |
| `test_tipo_invalido_vira_outro` | ✅ |  |
| `test_link_invalido_vira_vazio` | ✅ |  |
| `test_nao_e_evento_levanta_not_an_event` | ✅ |  |
| `test_sem_campos_obrigatorios_levanta_unprocessable` | ✅ |  |
| `test_data_invalida_conta_como_ausente` | ✅ |  |
| `test_json_invalido_levanta_erro_operacional` | ✅ |  |
| `test_falha_da_api_e_erro_operacional` | ✅ |  |
| `test_generate_chama_sdk_e_retorna_texto` | ✅ |  |
| `test_generate_encapsula_erro_do_sdk` | ✅ |  |

### `tests/test_metrics.py` — 6 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_from_counts_calcula_f1` | ✅ |  |
| `test_from_counts_sem_predicoes` | ✅ |  |
| `test_evaluate_corpus_extrator_perfeito` | ✅ |  |
| `test_evaluate_corpus_conta_erro_e_omissao` | ✅ |  |
| `test_baseline_parser_estruturado_no_corpus` | ✅ | O parser da US 4.1 serve de linha de base para a meta de 90% (US 4.2). |
| `test_evaluate_corpus_aceita_dataclass` | ✅ |  |

### `tests/test_minimizacao_lgpd.py` — 33 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_dominio_do_remetente[secretaria@cin.ufpe.br-cin.ufpe.br]` | ✅ |  |
| `test_dominio_do_remetente[Maria Souza <maria.souza.pessoal@cin.ufpe.br>-cin.ufpe.br]` | ✅ |  |
| `test_dominio_do_remetente["Souza, Maria" <Maria@CIn.UFPE.br>-cin.ufpe.br]` | ✅ |  |
| `test_dominio_do_remetente[<maria@cin.ufpe.br>-cin.ufpe.br]` | ✅ |  |
| `test_dominio_do_remetente[sem endere\xe7o-desconhecido]` | ✅ |  |
| `test_dominio_do_remetente[-desconhecido]` | ✅ |  |
| `test_dominio_do_remetente[None-desconhecido]` | ✅ |  |
| `test_dominio_do_remetente[maria@-desconhecido]` | ✅ |  |
| `test_mascara_dados_pessoais[fale com ana.lima+evento@gmail.com hoje-fale com [e-mail] hoje]` | ✅ |  |
| `test_mascara_dados_pessoais[CPF 123.456.789-09-CPF [cpf]]` | ✅ |  |
| `test_mascara_dados_pessoais[CPF 12345678909-CPF [cpf]]` | ✅ |  |
| `test_mascara_dados_pessoais[tel (81) 99999-8888-tel [telefone]]` | ✅ |  |
| `test_mascara_dados_pessoais[tel (81) 3333-4444-tel [telefone]]` | ✅ |  |
| `test_mascara_dados_pessoais[tel +55 81 99999-8888-tel [telefone]]` | ✅ |  |
| `test_mascara_dados_pessoais[tel 81 99999-8888-tel [telefone]]` | ✅ |  |
| `test_mascara_dados_pessoais[tel 99999-8888-tel [telefone]]` | ✅ |  |
| `test_mascara_dados_pessoais[a@b.com e c@d.org-[e-mail] e [e-mail]]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[Data: 2030-11-25 \xe0s 14:00]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[Semestre 2025-2026]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[Dia 25/11/2030, 14h30]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[Sala 2020, bloco A]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[https://forms.example.com/hack?id=123]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[Hackathon de 24 horas no CIn]` | ✅ |  |
| `test_mascara_nao_altera_dados_do_evento[]` | ✅ |  |
| `test_mascara_aceita_none` | ✅ |  |
| `test_log_guarda_so_o_dominio_do_remetente` | ✅ |  |
| `test_alerta_do_admin_nao_expoe_o_endereco_do_remetente` | ✅ |  |
| `test_extracted_data_do_log_sai_mascarado` | ✅ |  |
| `test_error_message_nao_carrega_dados_pessoais` | ✅ |  |
| `test_error_message_continua_cabendo_em_500_caracteres` | ✅ |  |
| `test_mensagem_de_erro_sem_dado_pessoal_nao_muda` | ✅ |  |
| `test_assinatura_e_remetente_nao_aparecem_em_nenhuma_tabela` | ✅ |  |
| `test_corpo_do_email_nao_vai_para_as_tabelas_extracao_e_email_associado` | ✅ |  |

### `tests/test_models_crud.py` — 35 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_usuario_defaults_do_banco` | ✅ |  |
| `test_usuario_dt_cadastro_usa_fuso_recife_independente_da_sessao[+00:00]` | ✅ |  |
| `test_usuario_dt_cadastro_usa_fuso_recife_independente_da_sessao[+14:00]` | ✅ |  |
| `test_usuario_dt_cadastro_usa_fuso_recife_independente_da_sessao[-11:00]` | ✅ |  |
| `test_usuario_email_duplicado_e_recusado` | ✅ |  |
| `test_usuario_campo_vazio_e_recusado[name]` | ✅ |  |
| `test_usuario_campo_vazio_e_recusado[email]` | ✅ |  |
| `test_usuario_campo_vazio_e_recusado[hashed_password]` | ✅ |  |
| `test_usuario_campo_vazio_e_recusado[profile_name]` | ✅ |  |
| `test_apagar_usuario_remove_favoritos_e_mantem_evento` | ✅ |  |
| `test_favorito_grava_e_le` | ✅ |  |
| `test_favorito_duplicado_e_recusado` | ✅ |  |
| `test_favorito_com_usuario_ou_evento_inexistente_e_recusado` | ✅ |  |
| `test_apagar_evento_remove_favoritos` | ✅ |  |
| `test_evento_defaults_do_banco` | ✅ |  |
| `test_evento_invalido_e_recusado[extra0]` | ✅ |  |
| `test_evento_invalido_e_recusado[extra1]` | ✅ |  |
| `test_evento_invalido_e_recusado[extra2]` | ✅ |  |
| `test_evento_invalido_e_recusado[extra3]` | ✅ |  |
| `test_evento_invalido_e_recusado[extra4]` | ✅ |  |
| `test_evento_de_email_aceita_link_vazio` | ✅ |  |
| `test_extracao_defaults_e_json_ida_e_volta` | ✅ |  |
| `test_extracao_aceita_os_seis_status[processado]` | ✅ |  |
| `test_extracao_aceita_os_seis_status[processado_ia]` | ✅ |  |
| `test_extracao_aceita_os_seis_status[ignorado]` | ✅ |  |
| `test_extracao_aceita_os_seis_status[nao_processado]` | ✅ |  |
| `test_extracao_aceita_os_seis_status[extracao_incompleta]` | ✅ |  |
| `test_extracao_aceita_os_seis_status[erro]` | ✅ |  |
| `test_extracao_status_invalido_e_recusado` | ✅ |  |
| `test_extracao_message_id_duplicado_ou_vazio_e_recusado` | ✅ |  |
| `test_extracao_event_id_so_com_status_processado` | ✅ |  |
| `test_extracao_event_id_inexistente_e_recusado` | ✅ |  |
| `test_apagar_evento_mantem_log_com_event_id_nulo` | ✅ |  |
| `test_apagar_log_mantem_evento` | ✅ |  |
| `test_truncate_entre_testes_zera_as_tabelas` | ✅ |  |

### `tests/test_models_vs_schema.py` — 16 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_conecta_no_banco` | ✅ |  |
| `test_tabelas_do_schema_existem` | ✅ |  |
| `test_cada_model_aponta_para_uma_tabela_do_schema` | ✅ |  |
| `test_colunas_do_model_existem_no_banco[usuario]` | ✅ |  |
| `test_colunas_do_model_existem_no_banco[events]` | ✅ |  |
| `test_colunas_do_model_existem_no_banco[extracao]` | ✅ |  |
| `test_colunas_do_model_existem_no_banco[favorito]` | ✅ |  |
| `test_colunas_do_banco_sem_model_nao_travam_insert[usuario]` | ✅ | Coluna que o model desconhece precisa ser opcional ou ter default, |
| `test_colunas_do_banco_sem_model_nao_travam_insert[events]` | ✅ | Coluna que o model desconhece precisa ser opcional ou ter default, |
| `test_colunas_do_banco_sem_model_nao_travam_insert[extracao]` | ✅ | Coluna que o model desconhece precisa ser opcional ou ter default, |
| `test_colunas_do_banco_sem_model_nao_travam_insert[favorito]` | ✅ | Coluna que o model desconhece precisa ser opcional ou ter default, |
| `test_chave_primaria_do_model_igual_a_do_banco[usuario]` | ✅ |  |
| `test_chave_primaria_do_model_igual_a_do_banco[events]` | ✅ |  |
| `test_chave_primaria_do_model_igual_a_do_banco[extracao]` | ✅ |  |
| `test_chave_primaria_do_model_igual_a_do_banco[favorito]` | ✅ |  |
| `test_chaves_estrangeiras_do_model_existem_no_banco` | ✅ |  |

### `tests/test_parser.py` — 7 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_extrai_todos_os_campos_obrigatorios` | ✅ |  |
| `test_aceita_data_iso` | ✅ |  |
| `test_aceita_data_por_extenso` | ✅ |  |
| `test_infere_tipo_por_palavra_chave` | ✅ |  |
| `test_email_sem_dados_obrigatorios_levanta_erro` | ✅ |  |
| `test_email_sem_local_levanta_erro` | ✅ |  |
| `test_email_vazio_de_titulo_usa_primeira_linha_do_corpo` | ✅ |  |

### `tests/test_parte_b_correcoes.py` — 22 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_login_aceita_email_maiusculo_e_com_espacos[ADMIN@CIN.UFPE.BR]` | ✅ |  |
| `test_login_aceita_email_maiusculo_e_com_espacos[  Admin@CIn.UFPE.br  ]` | ✅ |  |
| `test_post_e_put_rejeitam_registration_link_maior_que_500` | ✅ |  |
| `test_event_id_fora_do_int4_nao_gera_500[0]` | ✅ |  |
| `test_event_id_fora_do_int4_nao_gera_500[-1]` | ✅ |  |
| `test_event_id_fora_do_int4_nao_gera_500[2147483648]` | ✅ |  |
| `test_event_id_fora_do_int4_nao_gera_500[99999999999]` | ✅ |  |
| `test_x_user_id_fora_do_int4_nao_gera_500[0]` | ✅ |  |
| `test_x_user_id_fora_do_int4_nao_gera_500[-1]` | ✅ |  |
| `test_x_user_id_fora_do_int4_nao_gera_500[99999999999]` | ✅ |  |
| `test_extraction_alerts_valida_limit[1-200]` | ✅ |  |
| `test_extraction_alerts_valida_limit[0-422]` | ✅ |  |
| `test_extraction_alerts_valida_limit[-1-422]` | ✅ |  |
| `test_extraction_alerts_valida_limit[1000-422]` | ✅ |  |
| `test_extraction_alerts_valida_limit[abc-422]` | ✅ |  |
| `test_listagem_publica_oculta_evento_de_ontem_e_mantem_hoje_e_multidia` | ✅ |  |
| `test_parser_extrai_19_horas_prefixo_divulgacao_e_limites` | ✅ |  |
| `test_parser_estruturado_descarta_evento_no_passado` | ✅ |  |
| `test_falha_de_persistencia_faz_rollback_e_processa_proximo_email` | ✅ |  |
| `test_listar_favoritos_ordem_cronologica_filtra_inativos_e_expirados` | ✅ |  |
| `test_extraction_status_exige_admin_valida_limit_e_reflete_banco` | ✅ |  |
| `test_extraction_status_sinaliza_falha_do_gmail_e_limpa_ao_recuperar` | ✅ |  |

### `tests/test_roteiro_wallyson.py` — 24 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_gitignore_protege_segredos[backend/.env-True]` | ✅ |  |
| `test_gitignore_protege_segredos[backend/gmail_token.json-True]` | ✅ |  |
| `test_gitignore_protege_segredos[credentials.json-True]` | ✅ |  |
| `test_gitignore_protege_segredos[gemini_key.json-True]` | ✅ |  |
| `test_gitignore_protege_segredos[backend/chave.pem-True]` | ✅ |  |
| `test_gitignore_protege_segredos[backend/.env.example-False]` | ✅ |  |
| `test_seed_cria_admin_na_tabela_usuario` | ✅ |  |
| `test_seed_e_idempotente` | ✅ |  |
| `test_seed_nao_promove_usuario_comum` | ✅ |  |
| `test_login_senha_vazia_422` | ✅ |  |
| `test_jwt_expirado_ou_com_outra_chave_401[troque-esta-chave-em-producao-exp_delta0]` | ✅ |  |
| `test_jwt_expirado_ou_com_outra_chave_401[outra-chave-qualquer-exp_delta1]` | ✅ |  |
| `test_admin_rebaixado_perde_acesso_403` | ✅ |  |
| `test_criar_evento_na_data_de_hoje_recife` | ✅ |  |
| `test_criar_evento_com_espacos_ou_campo_ausente_422[title-   ]` | ✅ |  |
| `test_criar_evento_com_espacos_ou_campo_ausente_422[description-   ]` | ✅ |  |
| `test_criar_evento_com_espacos_ou_campo_ausente_422[location-   ]` | ✅ |  |
| `test_criar_evento_com_espacos_ou_campo_ausente_422[title-None]` | ✅ |  |
| `test_excluir_admin_criador_mantem_evento_com_admin_id_nulo` | ✅ |  |
| `test_limpeza_remove_favorito_do_evento_e_mantem_usuario` | ✅ |  |
| `test_cleanup_negado_para_usuario_comum_403` | ✅ |  |
| `test_cleanup_sem_reference_date_usa_hoje` | ✅ |  |
| `test_scheduler_em_modo_cron_diario` | ✅ |  |
| `test_job_de_limpeza_nao_quebra_com_excecao` | ✅ |  |

### `tests/test_validation_service.py` — 19 testes

| Teste | Res. | Descrição |
|---|---|---|
| `test_payload_integro_e_valido` | ✅ |  |
| `test_campos_obrigatorios_sao_titulo_e_data` | ✅ |  |
| `test_titulo_vazio_rejeita` | ✅ |  |
| `test_titulo_ausente_rejeita` | ✅ |  |
| `test_data_vazia_ou_ausente_rejeita` | ✅ |  |
| `test_data_impossivel_rejeita` | ✅ |  |
| `test_data_nao_string_rejeita` | ✅ |  |
| `test_formatos_de_data_aceitos` | ✅ |  |
| `test_titulo_e_data_invalidos_acumulam_motivos` | ✅ |  |
| `test_campos_extras_sao_ignorados` | ✅ |  |
| `test_coerce_date` | ✅ |  |
| `test_data_no_passado_e_descartada` | ✅ |  |
| `test_data_de_hoje_e_publicada` | ✅ |  |
| `test_data_futura_e_publicada` | ✅ |  |
| `test_titulo_ou_data_vazos_ja_sao_descartados` | ✅ |  |
| `test_estrutura_invalida_nao_acumula_motivo_temporal` | ✅ |  |
| `test_data_no_passado_sobre_estrutura_valida_e_o_unico_motivo` | ✅ |  |
| `test_padrao_usa_data_atual_de_recife` | ✅ |  |
| `test_decisao_publicar_quando_sem_motivos` | ✅ |  |

## 4. Frontend — `npm test` (node:test)

```text
ok 1 - gera e persiste um identificador anônimo no navegador
ok 2 - reaproveita o identificador anônimo nas visitas seguintes
ok 3 - visitante sem token vê Área do curador e vai para o login
ok 4 - curador autenticado vê Painel e vai para o painel
ok 5 - a janela padrão cobre hoje e os seis dias seguintes
ok 6 - selectUpcomingEvents filtra por janela e ordena por data e hora
ok 7 - selectUpcomingEvents devolve lista vazia quando não há eventos próximos
ok 8 - todayInRecife converte UTC para o fuso do Recife
ok 9 - formatDayLabel mostra dia e mês sem depender do fuso local
# tests 9
# pass 9
# fail 0
# skipped 0
```

## 5. Achados desta execução

### 5.1 `requirements.txt` não instala (já era o pendente P6)

`pip install -r requirements-dev.txt` → `ResolutionImpossible`: `google-genai==2.30.1` exige `pydantic>=2.12.5` e `httpx>=0.28`, mas o arquivo fixa `pydantic==2.9.2` e `httpx==0.27.2`. Quem instala só com o arquivo fica sem `google-genai` e **2 testes** de `test_gemini_client.py` (linhas 118 e 138) viram *skipped*. Instalando `pydantic 2.14.4` e `httpx 0.28.1` junto: **291 passed, 0 skipped**. Isso importa pro Docker (Albert): a imagem precisa de versões compatíveis. **Não alterei nada** — só registrei.

### 5.2 `Favoritebutton.test.jsx` não é executado

`npm test` roda só `node --test tests/services/*.test.js`. O teste de componente em `tests/components/events/` não entra (não há vitest/jsdom no `package.json`). Não foi rodado.

## 6. O que NÃO foi executado

- **Roteiro de Testes, Parte A (BD-001…BD-180) caso a caso:** não executei um a um. O que rodou acima são os testes automatizados que já existem; não foi feito o mapeamento BD-xxx ↔ teste.
- **Docker** (branch `feat/Dockerização-Deploy`) e **banco na nuvem**: não rodados (sem daemon Docker no sandbox; banco de nuvem ainda em construção pelo Albert).
- **Gmail/Gemini reais:** os testes usam fakes/mocks; nenhuma chave de API foi usada.
- **Ponta a ponta (jornada do usuário):** não feito — é a nova estratégia da semana.
