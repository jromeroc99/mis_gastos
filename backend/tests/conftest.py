"""
Configuración global de pytest para tests
"""
import os
import pytest
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Sobrescribir DATABASE_URL para tests
TEST_DATABASE_URL = "postgresql://mis_gastos_user:dev_password_123@localhost:5432/mis_gastos_test"

# Crear engine para tests
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,  # Menos verbose en tests
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Fixture de sesión que configura la base de datos de tests.
    Se ejecuta UNA VEZ al inicio de toda la suite de tests.
    """
    # Crear todas las tablas
    SQLModel.metadata.create_all(test_engine)
    
    yield
    
    # Limpiar todas las tablas al final de TODOS los tests
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def session():
    """
    Fixture que provee una sesión de base de datos para cada test.
    Hace rollback después de cada test para mantener aislamiento.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
