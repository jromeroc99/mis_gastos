# AGENTS.md - Guía de Desarrollo

## Misión del Agente

Actuar como partner técnico para desarrollar una aplicación de control de gastos personales, garantizando integridad de datos financieros y siguiendo mejores prácticas.

**IMPORTANTE**: El desarrollo debe ser secuencial y ordenado:
1. Primero completar el backend (FastAPI + PostgreSQL)
2. Después desarrollar el frontend (React + Vite)
3. Finalmente implementar la app móvil (Jetpack Compose)

No avanzar a la siguiente fase hasta que la anterior esté completamente funcional y probada.

**Metodología de Trabajo**:
- Ejecutar una tarea a la vez (task by task)
- Después de completar cada tarea, preguntar confirmación al usuario antes de continuar
- Esperar aprobación explícita antes de proceder con la siguiente tarea
- **Testing es obligatorio**: No avanzar a la siguiente tarea hasta que la actual tenga tests pasando correctamente

## Stack Tecnológico

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Base de Datos**: MySQL (simplicidad y facilidad de configuración)
- **Testing**: pytest

### Frontend
- **Framework**: React
- **Build Tool**: Vite
- **Styling**: Tailwind CSS

### Mobile (Fase 2)
- **Framework**: Jetpack Compose (Android)
- **Lenguaje**: Kotlin
- **Storage**: EncryptedSharedPreferences / Keystore

### Entorno de Desarrollo
- **Entorno**: WSL2
- **Base de Datos**: MySQL local (sin Docker por ahora)
- **Docker**: Se implementará al final, cuando todo funcione en local

### Decisiones de Diseño
- **Moneda**: EUR (sin multi-moneda por ahora)
- **Fechas de transacciones**: Solo DATE (sin hora) - el usuario solo registra el día
- **Auditoría**: created_at/updated_at usan TIMESTAMP para trazabilidad del sistema
- **APIs externas**: No usar APIs de precios por ahora (precio manual)

## Reglas Básicas

### 1. Python (Backend)
- Seguir PEP 8
- Usar Type Hints completos
- Documentar funciones con docstrings

```python
def calculate_total(transactions: list[Transaction]) -> Decimal:
    """Calculate total amount from transactions."""
    return sum(t.amount for t in transactions)
```

### 2. React (Frontend)
- Componentes funcionales con TypeScript
- Custom Hooks para lógica reutilizable

```typescript
export const ExpenseCard: FC<ExpenseCardProps> = ({ amount, description }) => {
  return <div>{description}: ${amount}</div>;
};
```

### 3. Manejo de Dinero (CRÍTICO)

**Siempre usar Decimal/NUMERIC para valores monetarios:**

```python
# Backend
from decimal import Decimal
amount: Decimal = Field(max_digits=12, decimal_places=2)
```

```sql
-- MySQL
amount DECIMAL(12, 2) NOT NULL
```

```typescript
// Frontend - recibir como string
interface Expense {
  amount: string;  // "99.99"
  currency: string;
}
```

### 4. Testing

**Proponer tests unitarios para toda lógica financiera:**

```python
async def test_calculate_total():
    expenses = [Expense(amount=Decimal('100.50'))]
    total = await service.calculate_monthly_total(user_id=1)
    assert total == Decimal('100.50')
```

### 5. WSL2

**Mantener proyecto en filesystem Linux:**
```bash
# ✅ Correcto
/home/username/projects/mis_gastos

# ❌ Evitar (latencia con Docker)
/mnt/d/dev/mis_gastos
```

---

**Versión**: 1.0.0
