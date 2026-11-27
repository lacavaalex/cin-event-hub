# Estratégia de testes

O projeto possui três superfícies de teste: banco de dados, backend e frontend. As suítes devem ser executadas contra ambientes descartáveis ou isolados.

## 1. Banco de dados

Local: `database/tests/` e `database/run_tests.py`.

O script aplica `database/001_schema.sql`, testa as constraints e relacionamentos, carrega os seeds de eventos, usuários, extrações e favoritos e repete os seeds para verificar idempotência. Os bancos temporários usados são `iesi_test_schema`, `iesi_test_seed` e `iesi_test_seeds`; eles são descartados ao final.

Comando na raiz:

```bash
pip install "psycopg[binary]"
python database/run_tests.py
```

O PostgreSQL deve estar acessível e o usuário precisa poder criar e remover bancos. Use `DATABASE_ADMIN_URL` para selecionar explicitamente o servidor de teste.

## 2. Backend

Local: `backend/tests/`.

A suíte usa pytest e PostgreSQL. A fixture de sessão cria `iesi_test_backend`, aplica o schema oficial, usa `Base.metadata.create_all` para os models e limpa as tabelas antes de cada teste. Ao final, o banco temporário é removido.

Comandos a partir de `backend/`:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

A fixture pode remover e recriar um banco com o nome `iesi_test_backend`. Nunca configure `DATABASE_ADMIN_URL` apontando para produção, homologação compartilhada ou uma base que contenha dados a preservar.

Os testes cobrem, entre outros aspectos, autenticação, operações administrativas de eventos, paginação, repositórios, expiração, extração, parsing, validação, duplicatas, minimização de dados e compatibilidade entre models e schema.

## 3. Frontend

Local: `frontend/tests/`.

O `package.json` usa o runner nativo do Node (`node --test`) nos testes de serviços.

Comandos a partir de `frontend/`:

```bash
npm ci
npm test
npm run lint
npm run build
```

Os testes presentes na branch analisada cobrem utilitários/serviços como navegação, identidade anônima e eventos futuros. O lint e o build complementam os testes unitários.

## 4. Verificação manual recomendada

Além das suítes automatizadas, validar no navegador e na API:

1. login administrativo válido, credencial inválida e usuário comum sem privilégio;
2. listagem pública, paginação, filtros, busca, detalhes e link de inscrição;
3. criação, edição e exclusão de eventos por administrador;
4. extração manual com Gmail configurado, incluindo mensagem válida, mensagem que não é evento, campos ausentes, data passada, lembrete duplicado e falha do provedor;
5. status e alertas de extração;
6. limpeza de evento vencido e preservação do log com `event_id` nulo;
7. acesso do frontend à API com a URL de ambiente configurada;
8. comportamento de tema e navegação após atualização direta de uma rota da SPA.

## 5. Integração contínua

Na árvore do repositório consultada em 27/11/2026, não foi identificado workflow versionado em `.github/workflows/`. Portanto, não se deve presumir que esses comandos estejam sendo executados automaticamente a cada push ou pull request. A equipe pode adicionar CI posteriormente para executar banco, backend, lint e build do frontend em pipeline.

## 6. Interpretação dos resultados

- `database/run_tests.py` retorna código `0` quando as etapas passam, `1` quando há falha e `2` quando não consegue conectar ao PostgreSQL.
- `pytest` deve terminar sem falhas; qualquer teste pulado deve ser entendido pelo motivo registrado no output.
- `npm test`, `npm run lint` e `npm run build` devem concluir com código zero.
- A aprovação das suítes não substitui a revisão dos itens de segurança e prontidão para produção descritos em `docs/operations/production-readiness.md`.
