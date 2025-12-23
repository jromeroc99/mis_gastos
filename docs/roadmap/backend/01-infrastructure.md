# Backend - Fase 1: Infraestructura Base

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 1.1: Configuración del Proyecto Python

**Objetivo**: Crear estructura base del proyecto backend con FastAPI

**Archivos a crear**:
```
backend/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

**Contenido de `requirements.txt`**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

**Contenido de `.env.example`**:
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mis_gastos

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

**Contenido inicial de `app/main.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mis Gastos API",
    version="1.0.0",
    description="API para control de gastos personales"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mis Gastos API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Testing**: 
```python
# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**Comandos de verificación**:
```bash
cd backend
pip install -r requirements.txt
pytest tests/test_main.py
uvicorn app.main:app --reload
```

**Criterio de aceptación**:
- ✅ Proyecto backend creado con estructura correcta
- ✅ FastAPI se ejecuta sin errores
- ✅ Tests pasan correctamente
- ✅ Endpoints `/` y `/health` responden correctamente

---

## Task 1.2: Configuración de PostgreSQL con Docker

**Objetivo**: Configurar PostgreSQL con Docker (solo DB al principio) y preparar dockerización completa para el futuro

**Estrategia**: Crear toda la configuración Docker desde el inicio, pero inicialmente solo levantar PostgreSQL. El backend se ejecuta localmente. Cuando todo esté funcional, ya tendremos todo listo para hacer `docker-compose up` completo.

**Archivos a crear**:
```
backend/
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

**Contenido de `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Contenido de `docker-compose.yml`**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: mis_gastos_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mis_gastos
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: mis_gastos_api
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/mis_gastos
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./app:/app/app  # Hot reload en desarrollo
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

**Contenido de `.dockerignore`**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.pytest_cache/
.coverage
htmlcov/
.env
.git
```

**Testing**:
```python
# tests/test_database_connection.py
import pytest
import os
from sqlmodel import create_engine, Session, text

def test_database_connection():
    """Test que la conexión a PostgreSQL funciona"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mis_gastos")
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        result = session.exec(text("SELECT 1 as test")).first()
        assert result[0] == 1
```

**Comandos de verificación (Fase inicial - Solo PostgreSQL)**:
```bash
# Levantar SOLO PostgreSQL
docker-compose up postgres -d

# Verificar que está corriendo
docker ps

# Ejecutar test de conexión (backend local)
pytest tests/test_database_connection.py

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Detener PostgreSQL
docker-compose down
```

**Comandos para dockerización completa (Fase final - después de Task 7.5)**:
```bash
# Construir y levantar TODO (PostgreSQL + Backend)
docker-compose up --build

# En otra terminal, ejecutar tests
docker-compose exec backend pytest

# Ver logs
docker-compose logs -f

# Detener todo
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

**Criterio de aceptación**:
- ✅ Archivos Docker creados (Dockerfile, docker-compose.yml, .dockerignore)
- ✅ PostgreSQL se levanta correctamente con Docker
- ✅ Base de datos `mis_gastos` creada automáticamente
- ✅ Backend local se conecta a PostgreSQL en Docker (localhost:5432)
- ✅ Test de conexión pasa correctamente
- ✅ Todo preparado para dockerización completa en el futuro

---

## Task 1.3: Configuración de SQLModel y Database Engine

**Objetivo**: Configurar SQLModel para ORM y gestión de sesiones

**Archivos a crear**:
```
backend/
├── app/
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       └── database.py
```

**Contenido de `app/core/config.py`**:
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Contenido de `app/core/database.py`**:
```python
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
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
```

**Testing**:
```python
# tests/test_database.py
import pytest
from app.core.database import engine, get_session
from sqlmodel import SQLModel, Session

def test_engine_creation():
    """Test que el engine se crea correctamente"""
    assert engine is not None
    assert str(engine.url).startswith("postgresql://")

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
```

**Actualizar `app/main.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables

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

@app.on_event("startup")
async def on_startup():
    """Inicializar base de datos al arrancar"""
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Mis Gastos API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Comandos de verificación**:
```bash
# Crear .env desde .env.example
cp .env.example .env

# Ejecutar tests
pytest tests/test_database.py

# Iniciar aplicación
uvicorn app.main:app --reload
```

**Criterio de aceptación**:
- ✅ Configuración cargada desde .env
- ✅ Engine de SQLModel creado correctamente
- ✅ get_session dependency funciona
- ✅ Tests pasan correctamente

---

**Próxima tarea**: [02-authentication.md](02-authentication.md) - Implementar sistema de autenticación JWT

**Nota**: NO avanzar hasta que todas las tareas de esta fase estén completas y testeadas.
