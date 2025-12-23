# Backend - Fase 7: Testing e Integración Final

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 7.1: Tests de Integración - Flujo Completo de Usuario

**Objetivo**: Crear tests end-to-end del flujo completo de la aplicación

**Archivos a crear**:
```
backend/
└── tests/
    └── integration/
        ├── __init__.py
        ├── test_user_flow.py
        └── test_financial_calculations.py
```

**Escenarios a testear**:

### Test: Usuario completo desde cero
1. Registrar usuario
2. Inicializar categorías por defecto
3. Crear cuentas bancarias
4. Crear transacciones (ingresos y gastos)
5. Obtener resumen financiero
6. Verificar balances correctos

### Test: Importación CSV completa
1. Registrar usuario
2. Importar CSV de transacciones
3. Importar CSV de activos
4. Importar CSV de pasivos
5. Verificar datos importados correctamente
6. Calcular patrimonio neto

### Test: Cálculos financieros complejos
1. Crear múltiples transacciones de diferentes tipos
2. Verificar desglose por categorías
3. Verificar exclusión de transferencias
4. Verificar cálculo de inversiones
5. Verificar tasa de ahorro

**Criterio de aceptación**:
- ✅ Todos los flujos end-to-end pasan
- ✅ Cálculos financieros son precisos (Decimal)
- ✅ No hay errores en integración de módulos

---

## Task 7.2: Tests de Carga y Performance

**Objetivo**: Verificar performance con datos realistas

**Escenarios**:
- Usuario con 1000+ transacciones
- Cálculo de resumen en < 500ms
- Importación CSV de 500 registros en < 2s

**Testing**:
```python
def test_performance_large_dataset():
    """Test con dataset grande"""
    # Crear 1000 transacciones
    # Medir tiempo de cálculo de resumen
    # Assert tiempo < 500ms
```

**Criterio de aceptación**:
- ✅ Queries optimizadas
- ✅ Tiempos de respuesta aceptables

---

## Task 7.3: Documentación de API (OpenAPI/Swagger)

**Objetivo**: Generar documentación completa de la API

**Funcionalidad**:
- FastAPI genera automáticamente docs en `/docs`
- Agregar descripciones a todos los endpoints
- Agregar ejemplos de request/response
- Documentar códigos de error

**Actualizar todos los endpoints con**:
```python
@router.post("/transactions", 
    response_model=TransactionResponse,
    summary="Crear nueva transacción",
    description="Crea una transacción bancaria y actualiza el balance de la cuenta",
    responses={
        201: {"description": "Transacción creada exitosamente"},
        400: {"description": "Datos inválidos"},
        401: {"description": "No autenticado"}
    }
)
```

**Criterio de aceptación**:
- ✅ Todos los endpoints documentados
- ✅ Ejemplos claros en Swagger UI
- ✅ Schemas con descripciones

---

## Task 7.4: Validaciones y Manejo de Errores

**Objetivo**: Implementar validaciones robustas y manejo de errores consistente

**Validaciones a implementar**:
- Validar que usuario solo accede a sus propios datos
- Validar rangos de fechas
- Validar que cuentas/categorías existen antes de crear transacción
- Validar tipos Decimal para montos
- Validar eliminación con confirmación

**Manejo de errores**:
```python
# Crear handler global de excepciones
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

**Testing obligatorio**:
- ✅ Test intentar acceder a datos de otro usuario (403)
- ✅ Test validaciones de tipos
- ✅ Test mensajes de error claros

---

## Task 7.5: Dockerización Completa del Backend

**Objetivo**: Dockerizar la aplicación completa (backend + PostgreSQL) para facilitar deployment

**Nota**: Esta tarea se realiza AL FINAL, después de tener el backend 100% funcional en desarrollo local.

**Archivos a crear**:
```
backend/
├── Dockerfile
├── docker-compose.yml (actualizar - añadir servicio backend)
└── .dockerignore
```

**Contenido de `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app
COPY ./tests ./tests

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Actualizar `docker-compose.yml`** (añadir servicio backend):
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
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./app:/app/app  # Hot reload en desarrollo
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

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
*.md
```
**Actualizar `backend/README.md`**:
```markdown
# Mis Gastos - Backend API

## Requisitos
- Python 3.11+
- PostgreSQL 15+
- Docker y Docker Compose (opcional, para deployment)

## Instalación y Desarrollo Local (Recomendado)

### 1. Configurar PostgreSQL en WSL2
```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Iniciar servicio
sudo service postgresql start

# Crear base de datos
sudo -u postgres psql -c "CREATE DATABASE mis_gastos;"
```

### 2. Configurar Backend
```bash
# Clonar repositorio y entrar a backend
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear .env desde .env.example
cp .env.example .env

# Ejecutar aplicación
uvicorn app.main:app --reload
```

### 3. Acceder a la API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Tests locales
pytest tests/ -v --cov=app

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v
```

## Deployment con Docker (Fase Final)

**Nota**: Usar Docker solo cuando el backend esté 100% funcional y testeado.

```bash
# Construir y levantar todo el stack (PostgreSQL + Backend)
docker-compose up --build

# En otra terminal, ejecutar tests
docker-compose exec backend pytest

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
**Comandos de verificación (Docker)**:
```bash
# Construir y levantar todos los servicios
docker-compose up --build

# Verificar que está corriendo
docker ps

# Ejecutar tests dentro del contenedor
docker-compose exec backend pytest

# Ver logs
docker-compose logs -f

# Acceder a la API
curl http://localhost:8000/health

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

**Criterio de aceptación**:
- ✅ Dockerfile construye correctamente
- ✅ docker-compose levanta PostgreSQL y backend
- ✅ Backend se conecta a PostgreSQL en Docker
- ✅ Tests pasan dentro del contenedor
- ✅ API accesible en http://localhost:8000
- ✅ Hot reload funciona con volumen montado
- ✅ Health checks implementados

---
- ✅ PostgreSQL conectado correctamente

---

## Task 7.6: README y Documentación de Deployment

**Objetivo**: Documentar cómo ejecutar y deployar el backend

**Actualizar `backend/README.md`**:
```markdown
# Mis Gastos - Backend API

## Requisitos
- Python 3.11+
- PostgreSQL 15+
- Docker y Docker Compose

## Instalación Local

1. Clonar repositorio
2. Crear .env desde .env.example
3. Instalar dependencias: `pip install -r requirements.txt`
4. Iniciar PostgreSQL: `docker-compose up -d`
5. Ejecutar aplicación: `uvicorn app.main:app --reload`

## Testing

```bash
pytest tests/ -v --cov=app
```

## Deployment con Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## API Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

**Criterio de aceptación**:
- ✅ README completo y claro
- ✅ Instrucciones de instalación funcionan
- ✅ Comandos de testing documentados

---

## Task 7.7: Checklist Final del Backend

**Verificación final antes de pasar a frontend**:

### Funcionalidad
- [ ] Autenticación JWT funcional
- [ ] CRUD completo de todos los modelos
- [ ] Cálculos financieros correctos
- [ ] Importación CSV funcional
- [ ] Onboarding completo

### Testing
- [ ] Cobertura de tests > 80%
- [ ] Tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Tests de performance aceptables

### Calidad de Código
- [ ] Seguir PEP 8
- [ ] Type hints completos
- [ ] Docstrings en funciones
- [ ] No warnings de linter

### Documentación
- [ ] API documentada en Swagger
- [ ] README actualizado
- [ ] Schemas con descripciones
- [ ] Ejemplos de uso

### Deployment
- [ ] Docker Compose funcional
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL con persistencia
- [ ] Health checks implementados

**IMPORTANTE**: NO avanzar a frontend hasta que TODOS los checkboxes estén marcados y el usuario confirme.

---

**Siguiente fase**: Frontend Web App (React + Vite)

**Ubicación**: `docs/roadmap/frontend/` - Se creará SOLO cuando backend esté 100% completado
