import datetime as dt  # noqa: F401
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.event import Event  # noqa: F401


class Favorite(Base):
    """Tabela 'favorito' do database/001_schema.sql.

    A chave primária é composta (id_usuario, id_events): o par já é único, então
    não há coluna ``id`` nem ``created_at``. Os atributos continuam ``user_id`` e
    ``event_id`` para não mudar o código dos repositórios.
    """

    __tablename__ = "favorito"

    user_id: Mapped[int] = mapped_column(
        "id_usuario", ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True
    )
    event_id: Mapped[int] = mapped_column(
        "id_events", ForeignKey("events.id_event", ondelete="CASCADE"), primary_key=True
    )
