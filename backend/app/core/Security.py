from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import JWT_ALGORITHM, SECRET_KEY

# tokenUrl é só metadado para a documentação do Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_admin_id(token: str = Depends(oauth2_scheme)) -> int:
    """Decodifica o JWT do administrador e devolve o ID (claim 'sub')."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None:
            raise _credentials_exception
    except JWTError:
        raise _credentials_exception

    try:
        return int(admin_id)
    except (ValueError, TypeError):
        return 1