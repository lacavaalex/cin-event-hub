"""Schemas Pydantic para eventos — contrato da API.

Compatível com os schemas da branch develop_alb (Albert).
"""

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EventType(StrEnum):
    """Tipos aceitos — alinhado com US 2.1 e filtro da US 3.2."""

    LECTURE = "Palestra"
    WORKSHOP = "Workshop"
    HACKATHON = "Hackathon"
    OTHER = "Outro"


class EventCreate(BaseModel):
    """Corpo do POST /events: todos os campos obrigatórios para criar um evento."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    date: dt.date
    time: dt.time
    location: str = Field(min_length=1, max_length=200)
    event_type: EventType
    registration_link: HttpUrl


class EventRead(BaseModel):
    """Resposta da API. ``from_attributes`` permite montar a partir do model ORM."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    date: dt.date
    time: dt.time
    location: str
    event_type: str
    registration_link: str
    status: str
    origin: str
