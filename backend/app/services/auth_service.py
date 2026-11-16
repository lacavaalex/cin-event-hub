"""Serviço de autenticação — regras de negócio do login (US 1.1).

O login é feito na tabela ``usuario`` (entidade USUARIO do modelo EER). Não há
mais tabela ``admins``: o administrador é o usuário com ``is_admin = TRUE``.
"""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories import user_repository


class InvalidCredentialsError(Exception):
    """E-mail ou senha inválidos."""


class NotAdminError(Exception):
    """Credenciais corretas, mas o usuário não é administrador."""


def authenticate_admin(db: Session, email: str, password: str) -> str:
    """Valida as credenciais de um usuário administrador e retorna um token JWT.

    Cenários cobertos (Gherkin da US 1.1):
    - Login bem-sucedido (usuário com ``is_admin``) → retorna token JWT
    - Credenciais inválidas → levanta InvalidCredentialsError
    - Usuário comum (``is_admin = FALSE``) → levanta NotAdminError
    """
    user = user_repository.get_by_email(db, email)

    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    if not user.is_admin:
        raise NotAdminError()

    return create_access_token(data={"sub": user.email, "uid": user.id})
