"""
Tests for security utilities
"""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)


def test_password_hashing():
    """Test que el hashing de passwords funciona"""
    password = "secretpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token_creation():
    """Test creación de access token"""
    data = {"sub": "[email protected]", "user_id": 1}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decodificar token
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "[email protected]"
    assert payload["user_id"] == 1
    assert payload["type"] == "access"


def test_refresh_token_creation():
    """Test creación de refresh token"""
    data = {"sub": "[email protected]", "user_id": 1}
    token = create_refresh_token(data)
    
    assert token is not None
    
    payload = decode_token(token)
    assert payload["type"] == "refresh"


def test_invalid_token():
    """Test que tokens inválidos retornan None"""
    invalid_token = "invalid.token.here"
    payload = decode_token(invalid_token)
    assert payload is None
