from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, links, redirect


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(redirect.router)
