"""Fixtures compartilhadas dos testes do backend.

Usa um SQLite em memória para não tocar no banco de desenvolvimento
(``backend/eventos.db``). Os models são importados explicitamente para que as
tabelas sejam registradas no ``Base.metadata`` antes do ``create_all``.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.admin import Admin  # noqa: F401 — registra a tabela admins
from app.models.event import Event  # noqa: F401 — registra a tabela events
from app.models.events.models import Favorite  # noqa: F401 — registra a tabela favorites
from app.models.extraction_log import ExtractionLog  # noqa: F401 — registra extraction_logs
from app.models.user import User  # noqa: F401 — registra a tabela users


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()