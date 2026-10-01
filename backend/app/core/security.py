"""Utilitários de segurança: hash de senhas e geração/validação de tokens JWT."""

import datetime as dt

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, SECRET_KEY

# ── Hashing de senhas ───────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Retorna o hash bcrypt da senha em texto puro."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Compara senha em texto puro com o hash armazenado."""
    return pwd_context.verify(plain, hashed)


# ── JWT ─────────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """Gera um token JWT com expiração configurável.

    O campo ``sub`` deve conter o e-mail do administrador.
    """
    to_encode = data.copy()
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodifica e valida um token JWT.

    Retorna o payload (dict) em caso de sucesso ou ``None`` se o token for
    inválido ou expirado.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
