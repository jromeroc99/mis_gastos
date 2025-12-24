"""
Tests for database configuration and session management
"""
import pytest
from app.core.database import engine, get_session
from sqlmodel import SQLModel, Session


def test_engine_creation():
    """Test que el engine se crea correctamente"""
    assert engine is not None
    assert str(engine.url).startswith("mysql+pymysql://")


def test_engine_database_name():
    """Test que el engine apunta a la base de datos correcta"""
    assert "mis_gastos" in str(engine.url)


def test_get_session():
    """Test que get_session retorna una sesión válida"""
    session_gen = get_session()
    session = next(session_gen)
    
    assert isinstance(session, Session)
    assert session.is_active
    
    # Cleanup
    try:
        next(session_gen)
    except StopIteration:
        pass
