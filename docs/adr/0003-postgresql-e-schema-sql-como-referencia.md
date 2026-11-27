# ADR — PostgreSQL como banco principal e SQL versionado como referência física

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

O backend precisa de integridade relacional real, constraints, chaves estrangeiras e testes que se comportem como o banco usado pela aplicação. Os testes anteriores com SQLite não exercitavam todas as regras do PostgreSQL.

## Decisão

Usar PostgreSQL em desenvolvimento, testes e produção. Manter `database/001_schema.sql` como referência das tabelas, constraints e índices físicos. Os models SQLAlchemy mapeiam as colunas existentes. A inicialização chama `Base.metadata.create_all`, mas isso não substitui a aplicação prévia do schema versionado nem constitui, por si só, um mecanismo de migração.

## Alternativas consideradas

- **SQLite como banco principal:** foi abandonado para evitar diferenças de constraints, tipos e comportamento entre teste e execução real.
- **Deixar apenas o ORM criar o schema:** não reproduziria automaticamente todas as constraints e índices parciais definidos no SQL atual.
- **Manter SQL e ORM com nomes diferentes sem mapeamento explícito:** aumentaria o risco de divergência; os models mapeiam os nomes reais das colunas.

## Consequências

A integridade crítica fica no PostgreSQL e os testes de banco/backend exercitam o mesmo SGBD. A preparação do ambiente exige aplicar o SQL antes do backend. A evolução do schema precisa atualizar SQL, models, seeds e testes em conjunto. Não foi identificado Alembic ou outro versionador automático de migrações na árvore analisada; alterações devem ser tratadas explicitamente pela equipe.

## Evidências na implementação

`database/001_schema.sql`, `backend/app/database/database.py`, `backend/app/models/`, `backend/app/main.py`, `backend/tests/conftest.py` e `database/run_tests.py`. O schema atual contém `usuario`, `events`, `extracao` e `favorito`.
