"""Serviço de autenticação — regras de negócio do login (US 1.1)."""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories import admin_repository


class InvalidCredentialsError(Exception):
    """E-mail ou senha inválidos."""


def authenticate_admin(db: Session, email: str, password: str) -> str:
    """Valida as credenciais do administrador e retorna um token JWT.

    Cenários cobertos (Gherkin da US 1.1):
    - Login bem-sucedido → retorna token JWT
    - Credenciais inválidas → levanta InvalidCredentialsError
    """
    admin = admin_repository.get_by_email(db, email)

    if admin is None or not verify_password(password, admin.hashed_password):
        raise InvalidCredentialsError()

    token = create_access_token(data={"sub": admin.email})
    return token
