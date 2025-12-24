"""
Tests for authentication and user schemas
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserBase, UserResponse
from datetime import datetime


def test_login_request_valid():
    """Test LoginRequest con datos válidos"""
    data = {
        "email": "test@gmail.com",
        "password": "password123"
    }
    login = LoginRequest(**data)
    assert login.email == "test@gmail.com"
    assert login.password == "password123"


def test_login_request_invalid_email():
    """Test LoginRequest con email inválido"""
    data = {
        "email": "invalid-email",
        "password": "password123"
    }
    with pytest.raises(ValidationError):
        LoginRequest(**data)


def test_user_create_valid():
    """Test UserCreate con datos válidos"""
    data = {
        "email": "john@gmail.com",
        "name": "John Doe",
        "password": "securepass123"
    }
    user = UserCreate(**data)
    assert user.email == "john@gmail.com"
    assert user.name == "John Doe"
    assert user.password == "securepass123"


def test_user_create_invalid_email():
    """Test UserCreate con email inválido"""
    data = {
        "email": "not-an-email",
        "name": "John Doe",
        "password": "securepass123"
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_token_response():
    """Test TokenResponse"""
    token = TokenResponse(
        access_token="eyJhbGc...",
        refresh_token="eyJhbGc..."
    )
    assert token.access_token == "eyJhbGc..."
    assert token.refresh_token == "eyJhbGc..."
    assert token.token_type == "bearer"


def test_token_response_custom_type():
    """Test TokenResponse con tipo personalizado"""
    token = TokenResponse(
        access_token="token1",
        refresh_token="token2",
        token_type="custom"
    )
    assert token.token_type == "custom"


def test_refresh_token_request():
    """Test RefreshTokenRequest"""
    refresh = RefreshTokenRequest(refresh_token="my.refresh.token")
    assert refresh.refresh_token == "my.refresh.token"


def test_user_base():
    """Test UserBase"""
    user = UserBase(
        email="testuser@gmail.com",
        name="Test User"
    )
    assert user.email == "testuser@gmail.com"
    assert user.name == "Test User"


def test_user_response():
    """Test UserResponse"""
    user = UserResponse(
        id=1,
        email="response@gmail.com",
        name="Test User",
        is_verified=False,
        is_active=True,
        created_at=datetime.now()
    )
    assert user.id == 1
    assert user.email == "response@gmail.com"
    assert user.name == "Test User"
    assert isinstance(user.created_at, datetime)
