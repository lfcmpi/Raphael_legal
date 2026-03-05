"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import engine
from api.db_models import Base
from api.routes.auth_routes import router as auth_router
from api.routes.cases_routes import router as cases_router
from api.routes.documents_routes import router as documents_router
from api.routes.users_routes import router as users_router
from api.routes.settings_routes import router as settings_router

_default_origins = "http://localhost:5173,http://localhost:3000"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", _default_origins).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Raphael Legal API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(users_router)
app.include_router(settings_router)
