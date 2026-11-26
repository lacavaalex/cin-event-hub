# syntax=docker/dockerfile:1
#
# Dockerfile do BACKEND (FastAPI/Python).
#
# Build em uma imagem "slim" (sem as ferramentas de compilação completas do
# Python "full"), o que deixa a imagem final bem menor — importante porque
# essa imagem é a que sobe para produção.

FROM python:3.12-slim AS base

# Evita que o Python escreva arquivos .pyc (lixo desnecessário dentro do
# container) e força os logs a saírem sem buffer, para aparecerem em tempo
# real no `docker logs` (senão o Python guarda a saída em memória antes de
# imprimir, o que é péssimo para debugar).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container. Tudo que vier depois (COPY,
# RUN, CMD) roda relativo a este caminho.
WORKDIR /app

# psycopg[binary] já traz o driver do PostgreSQL compilado, então não
# precisamos instalar libpq-dev/gcc aqui. Se um dia trocarmos para
# psycopg2 "puro" (sem o [binary]), essas duas linhas passam a ser
# necessárias antes do pip install:
#   RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
#    && rm -rf /var/lib/apt/lists/*

# Copiamos SÓ o requirements.txt primeiro (antes do resto do código).
# Isso é uma otimização de cache de camadas do Docker: enquanto o
# requirements.txt não mudar, o Docker reaproveita a camada do `pip
# install` em builds futuros, mesmo que o código da aplicação mude —
# economiza minutos a cada rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agora sim copiamos o resto do código da aplicação.
COPY . .

# Porta em que o Uvicorn vai escutar dentro do container. Isto é só
# documentação (não publica a porta sozinho) — quem de fato expõe a porta
# para fora é o docker-compose.yml, com `ports:`.
EXPOSE 8000

# Healthcheck: o compose/orquestrador consegue perguntar "este container
# está saudável?" chamando o endpoint /health que já existe no main.py.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando que sobe a API. "app.main:app" segue o padrão
# <pasta>.<arquivo>:<variável FastAPI>, batendo com backend/app/main.py.
# --host 0.0.0.0 é obrigatório: "127.0.0.1" só aceitaria conexões de
# dentro do próprio container, e o compose/frontend não conseguiria falar
# com a API.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
