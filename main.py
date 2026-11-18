"""Ponto de entrada da API (FastAPI).

Registra os routers de cada domínio e a configuração de CORS para o
frontend (Vite, porta padrão 5173) poder chamar a API em desenvolvimento.

"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.eventos.router import router as eventos_router
from app.api.favoritos.router import router as favoritos_router

# TODO: quando o router do IESI-29 (login/JWT) estiver disponível, importar
# e incluir aqui também, ex.:
#   from app.api.auth.router import router as auth_router
#   app.include_router(auth_router)

app = FastAPI(title="Sistema Integrador de Eventos Acadêmicos")

# As origens permitidas vêm de uma variável de ambiente (lista separada por
# vírgula), em vez de ficarem fixas no código. Isso é o que permite usar o
# MESMO Dockerfile/imagem em desenvolvimento (origem = localhost:5173) e em
# produção (origem = URL pública do frontend, ex.: Vercel/Netlify) só
# mudando o valor de ALLOWED_ORIGINS no ambiente de deploy, sem recompilar
# nada. Se a variável não for definida, cai no padrão de desenvolvimento.
_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in _allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eventos_router)
app.include_router(favoritos_router)


@app.get("/health")
def health_check():
    """Endpoint simples para confirmar que a API está de pé."""
    return {"status": "ok"}
