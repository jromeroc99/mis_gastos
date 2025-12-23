# Mis Gastos - Backend

API REST para control de gastos personales construida con FastAPI.

## Stack Tecnológico

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Base de Datos**: PostgreSQL
- **Testing**: pytest

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- pip

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Ejecución

### Modo desarrollo
```bash
uvicorn app.main:app --reload
```

La API estará disponible en: http://localhost:8000

### Documentación
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
```

Para ver coverage:
```bash
pytest --cov=app tests/
```

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── core/             # Configuración y database
│   ├── models/           # SQLModel models
│   ├── api/              # Endpoints
│   └── services/         # Lógica de negocio
├── tests/
├── requirements.txt
└── .env.example
```

## Reglas de Desarrollo

Ver [AGENTS.md](../AGENTS.md) para guías de desarrollo y mejores prácticas.
