from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./shortener.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# DATABASE_URL: aponta para um arquivo SQLite (shortener.db) que será criado na raiz do projeto.
# engine:a conexão com o banco
# SessionLocal: fábrica de sessões (cada requisição usa uma sessão própria).
# Base: classe da qual todos os models vão herdar.
# get_db(): abre uma sessão para a rota usar e garante que ela feche no final.
