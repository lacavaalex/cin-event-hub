"""Router de autenticação — POST /auth/login (US 1.1, IESI-29)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import InvalidCredentialsError, authenticate_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Autentica o administrador e retorna um token JWT.

    **US 1.1 — Critérios de Aceite:**
    - Login bem-sucedido → ``{ "token": "<jwt>" }``
    - Credenciais inválidas → HTTP 401 ``{ "detail": "Credenciais inválidas" }``
    - Campo vazio → HTTP 422 (validação automática do Pydantic)
    """
    try:
        token = authenticate_admin(db, body.email, body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    return LoginResponse(token=token)
