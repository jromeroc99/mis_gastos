"""
Test para verificar la conexión a PostgreSQL
"""
import pytest
import os
from sqlmodel import create_engine, Session, text


def test_database_connection():
    """Test que la conexión a PostgreSQL funciona"""
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://mis_gastos_user:dev_password_123@localhost:5432/mis_gastos"
    )
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        result = session.exec(text("SELECT 1 as test")).first()
        assert result[0] == 1


def test_database_exists():
    """Test que la base de datos mis_gastos existe y es accesible"""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://mis_gastos_user:dev_password_123@localhost:5432/mis_gastos"
    )
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        # Verificar que podemos consultar el nombre de la base de datos actual
        result = session.exec(text("SELECT current_database()")).first()
        assert result[0] == "mis_gastos"


def test_database_version():
    """Test que PostgreSQL está corriendo y verificar versión"""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://mis_gastos_user:dev_password_123@localhost:5432/mis_gastos"
    )
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        result = session.exec(text("SELECT version()")).first()
        assert result is not None
        assert "PostgreSQL" in result[0]
