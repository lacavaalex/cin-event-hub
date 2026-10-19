"""Alias para o serviço de expiração e limpeza de eventos."""

from app.services.events.cleanup_service import (
    CleanupReport,
    clean_expired_events,
    get_expired_events,
    is_event_expired,
)

__all__ = [
    "CleanupReport",
    "clean_expired_events",
    "get_expired_events",
    "is_event_expired",
]
