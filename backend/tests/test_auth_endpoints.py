"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, select
from app.main import app
from app.core.database import engine, create_db_and_tables
from app.models.user import User

client = TestClient(app)


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
        for user in session.exec(select(User)).all():
            session.delete(user)
        session.commit()


def test_register_user():
    """Test registro de usuario"""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@gmail.com",
        "name": "New User",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@gmail.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email():
    """Test que no se puede registrar email duplicado"""
    # Registrar primer usuario
    client.post("/api/v1/auth/register", json={
        "email": "duplicate@gmail.com",
        "name": "First User",
        "password": "password123"
    })
    
    # Intentar registrar con mismo email
    response = client.post("/api/v1/auth/register", json={
        "email": "duplicate@gmail.com",
        "name": "Second User",
        "password": "password456"
    })
    assert response.status_code == 400
    assert "Email ya registrado" in response.json()["detail"]


def test_login_success():
    """Test login exitoso"""
    # Primero registrar usuario
    client.post("/api/v1/auth/register", json={
        "email": "logintest@gmail.com",
        "name": "Login User",
        "password": "password123"
    })
    
    # Intentar login
    response = client.post("/api/v1/auth/login", json={
        "email": "logintest@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


def test_login_wrong_password():
    """Test login con contraseña incorrecta"""
    # Registrar usuario
    client.post("/api/v1/auth/register", json={
        "email": "wrongpass@gmail.com",
        "name": "Wrong Pass User",
        "password": "correctpassword"
    })
    
    # Intentar login con password incorrecta
    response = client.post("/api/v1/auth/login", json={
        "email": "wrongpass@gmail.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Email o contraseña incorrectos" in response.json()["detail"]


def test_login_nonexistent_user():
    """Test login con usuario que no existe"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 401


def test_get_me_with_token():
    """Test obtener información de usuario con token"""
    # Registrar y obtener token
    client.post("/api/v1/auth/register", json={
        "email": "metest@gmail.com",
        "name": "Me Test User",
        "password": "password123"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "metest@gmail.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Obtener información del usuario
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "metest@gmail.com"
    assert data["name"] == "Me Test User"
    assert "id" in data


def test_get_me_without_token():
    """Test que sin token no se puede acceder"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_get_me_with_invalid_token():
    """Test con token inválido"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_refresh_token():
    """Test renovar tokens con refresh token"""
    # Registrar y hacer login
    client.post("/api/v1/auth/register", json={
        "email": "refreshtest@gmail.com",
        "name": "Refresh User",
        "password": "password123"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "refreshtest@gmail.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Renovar token
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_with_invalid_token():
    """Test refresh con token inválido"""
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid.token.here"
    })
    assert response.status_code == 401
    assert "Refresh token inválido" in response.json()["detail"]


def test_refresh_with_access_token():
    """Test que no se puede usar access token para refresh"""
    # Registrar y hacer login
    client.post("/api/v1/auth/register", json={
        "email": "accesstoken@gmail.com",
        "name": "Access Token User",
        "password": "password123"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "accesstoken@gmail.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]
    
    # Intentar usar access token como refresh token
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": access_token
    })
    assert response.status_code == 401
    assert "Refresh token inválido" in response.json()["detail"]
