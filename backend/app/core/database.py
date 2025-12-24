"""
Database engine and session management using SQLModel
"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from .config import settings


# Engine con pool de conexiones
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries (desactivar en producción)
    pool_pre_ping=True,  # Verificar conexión antes de usar
)


def create_db_and_tables():
    """Crear todas las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLModel para operaciones de base de datos
    """
    with Session(engine) as session:
        yield session
