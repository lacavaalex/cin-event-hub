"""Configurações da aplicação."""
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cinevent.db")