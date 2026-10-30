from __future__ import annotations

# Instrução de sistema — fixa o papel e as regras de saída do modelo.
SYSTEM_INSTRUCTION = (
    "Você é um extrator de dados de eventos acadêmicos a partir de e-mails "
    "institucionais em português ou inglês. Extraia SOMENTE informações "
    "explicitamente presentes no e-mail; nunca invente dados. Responda "
    "exclusivamente com um objeto JSON válido, sem comentários e sem markdown."
)

# Schema JSON esperado. ``is_event`` separa "não é um e-mail de evento" (ignorar)
# de "é um evento, mas faltam dados" (não processado + alerta ao admin).
RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "is_event": {
            "type": "boolean",
            "description": "true se o e-mail divulga um evento acadêmico.",
        },
        "title": {"type": "string", "description": "Título do evento."},
        "date": {
            "type": "string",
            "description": "Data do evento no formato AAAA-MM-DD, ou vazio.",
        },
        "time": {
            "type": "string",
            "description": "Hora de início no formato HH:MM (24h), ou vazio.",
        },
        "location": {"type": "string", "description": "Local do evento, ou vazio."},
        "event_type": {
            "type": "string",
            "enum": ["Palestra", "Workshop", "Hackathon", "Outro"],
        },
        "description": {
            "type": "string",
            "description": "Resumo objetivo do evento (até 2000 caracteres).",
        },
        "registration_link": {
            "type": "string",
            "description": "URL de inscrição, se houver; senão, vazio.",
        },
    },
    "required": ["is_event", "title", "date", "time", "location"],
}

_TEMPLATE = """\
E-mail institucional recebido:

--- ASSUNTO ---
{subject}

--- CORPO ---
{body}

Extraia os campos do evento conforme o schema. Use "" (string vazia) quando o
dado não estiver no e-mail. Para date use AAAA-MM-DD e para time HH:MM.
"""


def build_prompt(subject: str, body: str) -> str:
    """Monta o prompt do usuário a partir do assunto e do corpo do e-mail."""
    return _TEMPLATE.format(subject=subject or "", body=body or "")
