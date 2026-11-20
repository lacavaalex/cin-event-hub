"""Schemas Pydantic para autenticação (login)."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Corpo do POST /auth/login. Senha vazia é recusada com 422 (US 1.1)."""
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    """Resposta do POST /auth/login — contrato esperado pelo frontend."""
    token: str
