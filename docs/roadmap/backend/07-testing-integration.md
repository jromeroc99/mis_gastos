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

## Task 7.5: Dockerización del Backend (POSPUESTA)

**Objetivo**: Dockerizar la aplicación completa cuando todo funcione en local

**IMPORTANTE**: Esta tarea se realizará AL FINAL del proyecto, cuando:
- ✅ Backend 100% funcional en local
- ✅ Todos los tests pasando
- ✅ Frontend integrado y funcionando
- ✅ Todo verificado sin contenedores

**Por ahora**: Trabajar con PostgreSQL local en WSL2 (sin Docker)

**Referencia futura**: Ver documentación en Phase 8 cuando se implemente.

---

## Resumen de Task 7 - Testing e Integración

### Requisitos previos
- Python 3.11+
- PostgreSQL 15+ (local en WSL2)
- pytest instalado

### Comandos de verificación (PostgreSQL local)

```bash
# Verificar PostgreSQL
sudo service postgresql status

# Acceder a la API
curl http://localhost:8000/health

# Ejecutar tests
pytest tests/ -v --cov=app

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

**Criterio de aceptación**:
- ✅ Tests unitarios e integración pasan
- ✅ Backend se conecta a PostgreSQL local
- ✅ API accesible en http://localhost:8000
- ✅ Hot reload funciona con uvicorn
- ✅ Health checks implementados
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
4. Iniciar PostgreSQL: `sudo service postgresql start`
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
