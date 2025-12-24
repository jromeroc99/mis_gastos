# Backend - Fase 2: Autenticación y Seguridad

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 2.1: Implementar Utilidades de Seguridad

**Objetivo**: Crear funciones para hashing de passwords y generación/verificación de JWT tokens

**Archivos a crear**:
```
backend/
├── app/
│   └── core/
│       └── security.py
```

**Contenido de `app/core/security.py`**:
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# Contexto para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear access token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crear refresh token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """Decodificar y verificar token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Testing**:
```python
# tests/test_security.py
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
```

**Comandos de verificación**:
```bash
pytest tests/test_security.py -v
```

**Criterio de aceptación**:
- ✅ Funciones de hashing implementadas y testeadas
- ✅ Generación de JWT tokens funciona correctamente
- ✅ Decodificación de tokens válida e inválida funciona
- ✅ Tests pasan correctamente

---

## Task 2.2: Crear Modelo de Usuario

**Objetivo**: Implementar modelo SQLModel para usuarios

**Archivos a crear**:
```
backend/
├── app/
│   └── models/
│       ├── __init__.py
│       └── user.py
```

**Contenido de `app/models/user.py`**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Contenido de `app/models/__init__.py`**:
```python
from .user import User

__all__ = ["User"]
```

**Actualizar `app/core/database.py`** para importar modelos:
```python
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from .config import settings

# Importar todos los modelos aquí para que SQLModel los conozca
from app.models import User  # noqa

# Engine con pool de conexiones
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

def create_db_and_tables():
    """Crear todas las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
```

**Testing**:
```python
# tests/test_user_model.py
import pytest
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Crear tablas antes de tests"""
    create_db_and_tables()
    yield

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
        
        # Intentar crear otro usuario con mismo email
        user2 = User(
            email="[email protected]",
            password_hash=get_password_hash("password456"),
            name="User Two"
        )
        session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
```

**Comandos de verificación**:
```bash
# Recrear base de datos (si es necesario)
sudo -u postgres psql -c "DROP DATABASE IF EXISTS mis_gastos;"
sudo -u postgres psql -c "CREATE DATABASE mis_gastos;"

# Ejecutar tests
pytest tests/test_user_model.py -v

# Verificar en PostgreSQL
psql -U mis_gastos_user -d mis_gastos -h localhost -c "\d users"
```

**Criterio de aceptación**:
- ✅ Modelo User creado correctamente
- ✅ Tabla `users` existe en PostgreSQL
- ✅ Tests de creación y unicidad pasan
- ✅ Campos tienen tipos correctos (Decimal para dinero NO aplica aquí)

---

## Task 2.3: Implementar Schemas de Autenticación

**Objetivo**: Crear schemas Pydantic para requests y responses de autenticación

**Archivos a crear**:
```
backend/
├── app/
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py
│       └── user.py
```

**Contenido de `app/schemas/user.py`**:
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Contenido de `app/schemas/auth.py`**:
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
```

**Contenido de `app/schemas/__init__.py`**:
```python
from .user import UserBase, UserCreate, UserResponse
from .auth import LoginRequest, TokenResponse, RefreshTokenRequest

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
]
```

**Testing**:
```python
# tests/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate

def test_login_request_valid():
    """Test LoginRequest con datos válidos"""
    data = {
        "email": "[email protected]",
        "password": "password123"
    }
    login = LoginRequest(**data)
    assert login.email == "[email protected]"
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
        "email": "[email protected]",
        "name": "John Doe",
        "password": "securepass123"
    }
    user = UserCreate(**data)
    assert user.email == "[email protected]"
    assert user.name == "John Doe"

def test_token_response():
    """Test TokenResponse"""
    token = TokenResponse(
        access_token="eyJhbGc...",
        refresh_token="eyJhbGc..."
    )
    assert token.token_type == "bearer"
```

**Comandos de verificación**:
```bash
pytest tests/test_schemas.py -v
```

**Criterio de aceptación**:
- ✅ Schemas creados y validación funciona
- ✅ EmailStr valida emails correctamente
- ✅ Tests de validación pasan
- ✅ Schemas siguen convención Request/Response

---

## Task 2.4: Implementar Endpoints de Autenticación

**Objetivo**: Crear endpoints para registro, login, refresh token

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── auth.py
│   └── middleware/
│       ├── __init__.py
│       └── auth.py
```

**Contenido de `app/middleware/auth.py`**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Dependency para obtener usuario actual desde token JWT"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tipo incorrecto"
        )
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user
```

**Contenido de `app/api/v1/auth.py`**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registrar nuevo usuario"""
    # Verificar si el email ya existe
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # Crear usuario
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password)
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """Login y obtener tokens JWT"""
    # Buscar usuario por email
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Crear tokens
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshTokenRequest, session: Session = Depends(get_session)):
    """Renovar access token usando refresh token"""
    payload = decode_token(refresh_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    user_id = payload.get("user_id")
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    # Crear nuevos tokens
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user
```

**Actualizar `app/main.py`** para incluir rutas:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.v1 import auth

app = FastAPI(
    title="Mis Gastos API",
    version="1.0.0",
    description="API para control de gastos personales"
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

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Mis Gastos API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Testing**:
```python
# tests/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import create_db_and_tables

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup():
    create_db_and_tables()

def test_register_user():
    """Test registro de usuario"""
    response = client.post("/api/v1/auth/register", json={
        "email": "[email protected]",
        "name": "New User",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "[email protected]"
    assert "id" in data

def test_register_duplicate_email():
    """Test que no se puede registrar email duplicado"""
    response = client.post("/api/v1/auth/register", json={
        "email": "[email protected]",
        "name": "Another User",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_success():
    """Test login exitoso"""
    response = client.post("/api/v1/auth/login", json={
        "email": "[email protected]",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    """Test login con contraseña incorrecta"""
    response = client.post("/api/v1/auth/login", json={
        "email": "[email protected]",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_me_with_token():
    """Test obtener información de usuario con token"""
    # Primero login
    login_response = client.post("/api/v1/auth/login", json={
        "email": "[email protected]",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Luego obtener info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "[email protected]"

def test_get_me_without_token():
    """Test que sin token no se puede acceder"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403
```

**Comandos de verificación**:
```bash
# Recrear base de datos
docker-compose down -v
docker-compose up -d

# Ejecutar tests
pytest tests/test_auth_endpoints.py -v

# Probar manualmente
uvicorn app.main:app --reload
```

**Criterio de aceptación**:
- ✅ Endpoint /register crea usuarios correctamente
- ✅ Endpoint /login retorna tokens JWT
- ✅ Endpoint /refresh renueva tokens
- ✅ Endpoint /me retorna usuario autenticado
- ✅ Todos los tests pasan correctamente

---

**Próxima tarea**: [03-models.md](03-models.md) - Implementar modelos de datos principales

**Nota**: NO avanzar hasta que todas las tareas de autenticación estén completas y testeadas.
