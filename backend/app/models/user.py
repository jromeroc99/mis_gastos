"""
User model for authentication and user management
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class User(SQLModel, table=True):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    is_verified: bool = Field(default=False)  # Email verificado
    is_active: bool = Field(default=True)  # Control de acceso
    verification_code: Optional[str] = Field(default=None, max_length=6)  # Código temporal (6 dígitos)
    verification_expires: Optional[datetime] = Field(default=None)  # Expiración del código
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
