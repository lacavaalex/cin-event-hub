"""Schemas Pydantic para autenticação (login)."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Corpo do POST /auth/login."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Resposta do POST /auth/login — contrato esperado pelo frontend."""
    token: str
