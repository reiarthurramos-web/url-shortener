from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_token(token)
    user = db.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# OAuth2PasswordBearer(tokenUrl="/auth/login"): lê o token do cabeçalho Authorization: Bearer ... e faz o botão Authorize aparecer no Swagger (/docs). O tokenUrl aponta para a rota de login que vamos criar no próximo passo.
# get_current_user: recebe o token e uma sessão do banco, decodifica o token e busca o usuário pelo id.
# HTTPException(401): é o erro devolvido quando o token não vale ou o usuário não existe mais.
