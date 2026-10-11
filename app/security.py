import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao-0123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


# SECRET_KEY: a chave que assina os tokens. Ela lê a variável de ambiente SECRET_KEY e, se não existir, usa um valor padrão (serve para desenvolver, mas em produção precisa ser uma chave forte e secreta).
# hash_password: transforma a senha em hash para guardar no banco.
# verify_password: confere se a senha digitada no login bate com o hash.
# create_access_token: cria o JWT com o id do usuário (sub) e validade de 60 minutos (exp).
# decode_token: lê o token e devolve o id do usuário. Se o token for inválido ou estiver expirado, devolve None.
