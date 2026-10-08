import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# tokenUrl é só metadado para a documentação do Swagger; ajustar se o
# endpoint de login tiver outro caminho.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_admin_id(token: str = Depends(oauth2_scheme)) -> int:
    """Decodifica o JWT do administrador e devolve o ID (claim "sub")."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None:
            raise _credentials_exception
    except JWTError:
        raise _credentials_exception

    return int(admin_id)