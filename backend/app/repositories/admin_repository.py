"""Repositório de administradores — acesso direto ao banco de dados."""

from sqlalchemy.orm import Session

from app.models.admin import Admin


def get_by_email(db: Session, email: str) -> Admin | None:
    """Busca um administrador pelo e-mail."""
    return db.query(Admin).filter(Admin.email == email).first()


def create(db: Session, email: str, hashed_password: str) -> Admin:
    """Insere um novo administrador no banco."""
    admin = Admin(email=email, hashed_password=hashed_password)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
