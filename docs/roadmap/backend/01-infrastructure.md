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
pymysql==1.1.0
cryptography==41.0.7
PyJWT[crypto]==2.8.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
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
DATABASE_URL=mysql+pymysql://mis_gastos_user:dev_password_123@localhost/mis_gastos

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

## Task 1.2: Configuración de MySQL Local

**Objetivo**: Configurar MySQL localmente en WSL2 para desarrollo

**Estrategia**: Usar MySQL nativo instalado en WSL2. Docker se implementará al final cuando todo funcione.

**Instalación de MySQL en WSL2**:
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar MySQL
sudo apt install mysql-server -y

# Iniciar servicio
sudo service mysql start

# Verificar status
sudo service mysql status
```

**Configuración inicial de la base de datos**:
```bash
# Usar el script SQL proporcionado
cd backend
sudo mysql < setup_mysql.sql

# O manualmente:
sudo mysql

# Crear base de datos y usuario (ejecutar en MySQL)
CREATE DATABASE mis_gastos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE mis_gastos_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mis_gastos_user'@'localhost' IDENTIFIED BY 'dev_password_123';
GRANT ALL PRIVILEGES ON mis_gastos.* TO 'mis_gastos_user'@'localhost';
GRANT ALL PRIVILEGES ON mis_gastos_test.* TO 'mis_gastos_user'@'localhost';
FLUSH PRIVILEGES;

# Salir de MySQL
exit;
```

**Archivo `.env` en `backend/`**:
```env
# Database
DATABASE_URL=mysql+pymysql://mis_gastos_user:dev_password_123@localhost/mis_gastos

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Testing**:
```python
# tests/test_database_connection.py
import pytest
import os
from sqlmodel import create_engine, Session, text

def test_database_connection():
    """Test que la conexión a MySQL funciona"""
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://mis_gastos_user:dev_password_123@localhost/mis_gastos")
    engine = create_engine(database_url)
    
    with Session(engine) as session:
        result = session.exec(text("SELECT 1 as test")).first()
        assert result[0] == 1
```

**Comandos de verificación**:
```bash
# Verificar que MySQL está corriendo
sudo service mysql status

# Conectar a la base de datos
mysql -u mis_gastos_user -pdev_password_123 mis_gastos

# Ejecutar test de conexión
cd backend
source venv/bin/activate
pytest tests/test_database_connection.py

# Ver bases de datos existentes
mysql -u root -e "SHOW DATABASES;"
```

**Comandos útiles de MySQL**:
```bash
# Iniciar servicio
sudo service mysql start

# Detener servicio
sudo service mysql stop

# Reiniciar servicio
sudo service mysql restart

# Ver logs
sudo tail -f /var/log/mysql/error.log
```

**Criterio de aceptación**:
- ✅ MySQL instalado en WSL2
- ✅ Bases de datos `mis_gastos` y `mis_gastos_test` creadas correctamente
- ✅ Usuario y permisos configurados
- ✅ Backend local se conecta a MySQL (localhost:3306)
- ✅ Test de conexión pasa correctamente
- ✅ Archivo `.env` configurado

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
    pool_recycle=3600,  # Reciclar conexiones cada hora (MySQL timeout)
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
    assert str(engine.url).startswith("mysql+pymysql://")

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
