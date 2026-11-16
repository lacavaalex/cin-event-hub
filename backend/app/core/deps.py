"""Dependências do FastAPI para proteger rotas que exigem autenticação."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories import user_repository

_bearer = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Valida o JWT do header ``Authorization: Bearer <token>`` e devolve o administrador.

    O ``sub`` do token é o e-mail do usuário. O usuário precisa existir na tabela
    ``usuario`` e continuar com ``is_admin = TRUE`` (se perder o perfil ou for
    removido, o token deixa de valer).

    - Token ausente, inválido ou expirado → HTTP 401
    - Usuário inexistente ou que não é administrador → HTTP 403
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = user_repository.get_admin_by_email(db, payload["sub"])
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return admin
