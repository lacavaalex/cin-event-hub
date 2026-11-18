"""Repositório de usuários — acesso direto à tabela ``usuario``.

Segue o modelo EER/relacional (``docs/Diagrama_BD/modeloRelacionalIESI``): não
existe entidade própria de administrador. Administrador é um ``usuario`` com
``is_admin = TRUE``.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    """Busca um usuário pelo e-mail (único na tabela ``usuario``)."""
    return db.scalar(select(User).where(User.email == email))


def get_by_id(db: Session, user_id: int) -> User | None:
    """Busca um usuário pela chave primária da tabela ``usuario``."""
    return db.get(User, user_id)


def get_admin_by_email(db: Session, email: str) -> User | None:
    """Busca um usuário administrador (``is_admin = TRUE``) pelo e-mail."""
    return db.scalar(select(User).where(User.email == email, User.is_admin.is_(True)))


def create(
    db: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    profile_name: str,
    is_admin: bool = False,
) -> User:
    """Insere um novo usuário. ``dt_cadastro`` é preenchida pelo banco."""
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        profile_name=profile_name,
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
