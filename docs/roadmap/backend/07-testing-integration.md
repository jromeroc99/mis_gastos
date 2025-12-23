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

## Task 7.5: Docker Compose Completo (Desarrollo y Producción)

**Objetivo**: Configurar Docker Compose para desarrollo y producción con backend + PostgreSQL

**Archivos a crear/actualizar**:
```
backend/
├── Dockerfile
├── docker-compose.dev.yml (actualizar - ya existe solo con postgres)
├── docker-compose.prod.yml (actualizar - ya existe solo con postgres)
└── .dockerignore
```

**Contenido de `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Actualizar `docker-compose.dev.yml`** (Desarrollo completo):
```yaml
version: '3.8'

services:
  # Backend API en desarrollo
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mis_gastos_api_dev
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mis_gastos_dev
**Contenido de `.env.prod.example`** (crear para producción):
```bash
# Environment
ENV=production

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_THIS_SECURE_PASSWORD
POSTGRES_DB=mis_gastos

# Security - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Ajustar según dominio
**Actualizar `backend/README.md`**:
```markdown
# Mis Gastos - Backend API

## Requisitos
- Python 3.11+
- PostgreSQL 15+
- Docker y Docker Compose

## Instalación Local (sin Docker)

1. Clonar repositorio
2. Crear .env desde .env.example
3. Instalar dependencias: `pip install -r requirements.txt`
4. Iniciar PostgreSQL: `docker-compose -f docker-compose.dev.yml up -d postgres`
5. Ejecutar aplicación: `uvicorn app.main:app --reload`

## Desarrollo con Docker (Recomendado)

```bash
# Levantar todo el stack de desarrollo (API + PostgreSQL)
docker-compose -f docker-compose.dev.yml up --build

# Acceder a la API
http://localhost:8000/docs

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f

# Detener
docker-compose -f docker-compose.dev.yml down
```

## Testing

```bash
# Tests locales
pytest tests/ -v --cov=app

# Tests en contenedor
docker-compose -f docker-compose.dev.yml exec api pytest tests/ -v
```

## Producción con Docker

```bash
# 1. Crear archivo .env.prod con variables seguras
cp .env.prod.example .env.prod
# Editar .env.prod con valores de producción

# 2. Levantar en modo producción
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 3. Verificar estado
docker-compose -f docker-compose.prod.yml ps

# 4. Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# 5. Detener
docker-compose -f docker-compose.prod.yml down
```

## Diferencias entre Entornos

| Característica | Desarrollo | Producción |
|---------------|------------|------------|
| Puerto PostgreSQL | 5432 | 5433 |
| Base de datos | mis_gastos_dev | mis_gastos |
| Hot reload | ✅ Sí | ❌ No |
| Variables .env | Hardcoded en compose | Desde .env.prod |
| Logs SQL | ✅ Verbose | ❌ Minimal |
| Health checks | Básicos | Completos |

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
```ker-compose -f docker-compose.prod.yml down
```

**Criterio de aceptación**:
- ✅ Desarrollo y producción con configuraciones separadas
- ✅ Hot reload funciona en desarrollo (volumen montado)
- ✅ Producción usa variables de entorno seguras
- ✅ PostgreSQL en diferentes puertos (5432 dev, 5433 prod)
- ✅ Redes aisladas para cada entorno
- ✅ Health checks implementados
- ✅ Restart policies configuradas
      - mis_gastos_network_dev
    restart: unless-stopped

  # PostgreSQL para desarrollo
  postgres:
    image: postgres:15-alpine
    container_name: mis_gastos_db_dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mis_gastos_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - mis_gastos_network_dev

volumes:
  postgres_data_dev:

networks:
  mis_gastos_network_dev:
    driver: bridge
```

**Actualizar `docker-compose.prod.yml`** (Producción completa):
```yaml
version: '3.8'

services:
  # Backend API en producción
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mis_gastos_api_prod
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      - REFRESH_TOKEN_EXPIRE_DAYS=${REFRESH_TOKEN_EXPIRE_DAYS:-7}
      - CORS_ORIGINS=${CORS_ORIGINS:-["http://localhost:5173"]}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - mis_gastos_network_prod
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL para producción
  postgres:
    image: postgres:15-alpine
    container_name: mis_gastos_db_prod
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5433:5432"  # Puerto diferente para no conflictuar con dev
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - mis_gastos_network_prod

volumes:
  postgres_data_prod:

networks:
  mis_gastos_network_prod:
    driver: bridge
```

**Testing**:
```bash
docker-compose -f docker-compose.prod.yml up --build
curl http://localhost:8000/health
```

**Criterio de aceptación**:
- ✅ Aplicación se ejecuta en contenedor
- ✅ Variables de entorno configurables
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
