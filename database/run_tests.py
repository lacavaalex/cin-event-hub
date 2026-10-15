#!/usr/bin/env python3
"""Testes do banco de dados: o equivalente do `npm test` para a pasta database/.

Como rodar (na raiz do repositório):
    pip install "psycopg[binary]"
    python database/run_tests.py

Precisa de um PostgreSQL 13+ acessível. Por padrão o script conecta em
    postgresql://postgres:dev@localhost:5432/postgres
Para usar outro servidor, defina DATABASE_ADMIN_URL
(PowerShell: $env:DATABASE_ADMIN_URL = "postgresql://usuario:senha@host:5432/postgres").
Para subir um PostgreSQL descartável com Docker:
    docker run --rm --name pg-test -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:16

O script cria bancos temporários (iesi_test_*), roda schema, seed e testes e
apaga os bancos no final. Nenhum outro banco do servidor é alterado.
Código de saída: 0 = tudo passou, 1 = algum teste falhou, 2 = sem conexão.
"""

import os
import pathlib
import sys

try:
    import psycopg
    from psycopg.conninfo import make_conninfo
except ImportError:
    print('Falta o driver do PostgreSQL: pip install "psycopg[binary]"', file=sys.stderr)
    sys.exit(2)

BASE = pathlib.Path(__file__).resolve().parent
ADMIN_URL = os.environ.get(
    "DATABASE_ADMIN_URL", "postgresql://postgres:dev@localhost:5432/postgres"
)

# (nome da etapa, banco temporário, [(arquivo, descrição do passo), ...])
# Uma etapa só roda se todos os arquivos dela existem (ex.: a branch ainda
# não tem o seed).
ETAPAS = [
    ("Schema (IESI-56)", "iesi_test_schema", [
        ("001_schema.sql", "aplicar o schema"),
        ("tests/001_schema_test.sql", "testar restrições e relacionamentos"),
    ]),
    ("Seed (IESI-57)", "iesi_test_seed", [
        ("001_schema.sql", "aplicar o schema"),
        ("002_seed_eventos.sql", "aplicar o seed"),
        ("tests/002_seed_test.sql", "testar o seed"),
        ("002_seed_eventos.sql", "rodar o seed de novo"),
        ("tests/002_seed_test.sql", "testar de novo (nada pode duplicar)"),
    ]),
]


def executar_etapa(admin, banco, passos):
    """Roda os passos num banco temporário. Devolve (passou, verificações ok)."""
    admin.execute(f'DROP DATABASE IF EXISTS "{banco}"')
    admin.execute(f'CREATE DATABASE "{banco}"')
    verificacoes = 0
    conn = None
    try:
        conn = psycopg.connect(make_conninfo(ADMIN_URL, dbname=banco), autocommit=True)

        def aviso(diag):
            nonlocal verificacoes
            mensagem = diag.message_primary or ""
            if mensagem.startswith("ok: "):
                verificacoes += 1
                print(f"        ok  {mensagem[4:]}")

        conn.add_notice_handler(aviso)
        for arquivo, descricao in passos:
            print(f"    > {descricao}")
            try:
                conn.execute((BASE / arquivo).read_text(encoding="utf-8"))
            except psycopg.Error as erro:
                motivo = erro.diag.message_primary or str(erro).strip().splitlines()[0]
                print(f"    X {motivo}")
                return False, verificacoes
        return True, verificacoes
    finally:
        if conn is not None:
            conn.close()
        admin.execute(f'DROP DATABASE IF EXISTS "{banco}"')


def main():
    try:  # evita erro de acentuação no terminal do Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    try:
        admin = psycopg.connect(ADMIN_URL, autocommit=True)
    except psycopg.OperationalError as erro:
        print("Não consegui conectar no PostgreSQL:", str(erro).strip().splitlines()[0], file=sys.stderr)
        print("Suba um com Docker (comando no topo deste arquivo) ou defina DATABASE_ADMIN_URL.", file=sys.stderr)
        return 2

    tudo_certo, total = True, 0
    with admin:
        for nome, banco, passos in ETAPAS:
            if not all((BASE / arquivo).exists() for arquivo, _ in passos):
                continue
            print(nome)
            passou, verificacoes = executar_etapa(admin, banco, passos)
            total += verificacoes
            tudo_certo = tudo_certo and passou
            print(f"  {'PASSOU' if passou else 'FALHOU'}\n")

    print(f"Resultado: {'TUDO PASSOU' if tudo_certo else 'HOUVE FALHAS'} ({total} verificações ok)")
    return 0 if tudo_certo else 1


if __name__ == "__main__":
    sys.exit(main())
