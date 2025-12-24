from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup: crear tablas en la base de datos
    create_db_and_tables()
    yield
    # Shutdown: limpieza si es necesaria


app = FastAPI(
    title="Mis Gastos API",
    version="1.0.0",
    description="API para control de gastos personales",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Mis Gastos API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
