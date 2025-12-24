"""
Tests for User model
"""
import pytest
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError
from app.core.database import engine, create_db_and_tables
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Crear tablas antes de tests y limpiar después"""
    # Limpiar cualquier tabla existente
    SQLModel.metadata.drop_all(engine)
    # Crear tablas frescas
    create_db_and_tables()
    yield
    # Limpiar después de los tests
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_data():
    """Limpiar datos entre tests"""
    yield
    # Limpiar usuarios después de cada test
    with Session(engine) as session:
        session.exec(select(User)).all()
        for user in session.exec(select(User)).all():
            session.delete(user)
        session.commit()


def test_create_user():
    """Test crear usuario en base de datos"""
    with Session(engine) as session:
        user = User(
            email="[email protected]",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "[email protected]"
        assert user.name == "Test User"
        assert user.created_at is not None
        assert user.updated_at is not None


def test_user_email_unique():
    """Test que el email es único"""
    with Session(engine) as session:
        user1 = User(
            email="[email protected]",
            password_hash=get_password_hash("password123"),
            name="User One"
        )
        session.add(user1)
        session.commit()
        
    # Intentar crear otro usuario con mismo email en una nueva sesión
    with Session(engine) as session:
        user2 = User(
            email="[email protected]",
            password_hash=get_password_hash("password456"),
            name="User Two"
        )
        session.add(user2)
        
        with pytest.raises(IntegrityError):
            session.commit()

