"""Model ORM do usuário (tabela 'usuario').

A tabela é criada pelo ``database/001_schema.sql``; este model só a mapeia no
SQLAlchemy, com nomes de atributo em inglês e o nome real da coluna como primeiro
argumento de ``mapped_column``. Ele é necessário porque ``favorito.id_usuario``
aponta para ``usuario``: sem o model, o ``Base.metadata.create_all`` falha com
NoReferencedTableError e a aplicação não sobe.
"""

import datetime as dt

from sqlalchemy import Boolean, Date, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column("id_usuario", primary_key=True)
    name: Mapped[str] = mapped_column("nome", String(90))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column("senha_hash", String(100))
    profile_name: Mapped[str] = mapped_column("nome_perfil", String(50))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[dt.date] = mapped_column(
        "dt_cadastro", Date, server_default=func.current_date()
    )
