"""Schemas Pydantic: o "contrato" da API para eventos."""
import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EventType(StrEnum):
    """Tipos aceitos. Alinhar com a US 2.1 e com o filtro da US 3.2."""

    LECTURE = "Palestra"
    WORKSHOP = "Workshop"
    HACKATHON = "Hackathon"
    OTHER = "Outro"


class EventUpdate(BaseModel):
    """Corpo do PUT /events/{id}: a representação completa dos campos editáveis."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    date: dt.date
    time: dt.time
    location: str = Field(min_length=1, max_length=200)
    event_type: EventType
    registration_link: HttpUrl


class EventRead(BaseModel):
    """Resposta da API. `from_attributes` permite montar a partir do model ORM."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    date: dt.date
    time: dt.time
    location: str
    event_type: EventType
    registration_link: str
    status: str
    origin: str
