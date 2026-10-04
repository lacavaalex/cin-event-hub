"""Dependência do FastAPI para proteger rotas que exigem autenticação."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token

_bearer = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Extrai e valida o token JWT do header ``Authorization: Bearer <token>``.

    Retorna o payload do token (contém ``sub`` com o e-mail do admin).
    Levanta HTTP 401 se o token for ausente, inválido ou expirado.
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
