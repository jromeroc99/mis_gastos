# Backend - Fase 5: Lógica de Negocio

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 5.1: Servicio de Cálculo de Balances

**Objetivo**: Implementar servicio para cálculos de balances y resúmenes financieros

**Archivos a crear**:
```
backend/
├── app/
│   └── services/
│       ├── __init__.py
│       └── balance.py
```

**Funciones a implementar**:
- `calculate_account_balance(account_id: int) -> Decimal`
- `calculate_total_balance(user_id: int) -> Decimal`
- `calculate_period_summary(user_id: int, start: date, end: date) -> dict`

**Testing obligatorio**:
- ✅ Test cálculo de balance de cuenta
- ✅ Test cálculo de balance total del usuario
- ✅ Test resumen de periodo con ingresos/gastos/ahorro

**Reglas de negocio**:
- Considerar tipos de categorías: regular, transfer, investment
- Ahorro líquido = balance_final - balance_inicial
- Ahorro total = ahorro_líquido + inversiones

---

## Task 5.2: Servicio de Cálculo de Activos

**Objetivo**: Implementar cálculos de cantidad y precio promedio de activos

**Archivos a crear**:
```
backend/
├── app/
│   └── services/
│       └── asset_calculator.py
```

**Funciones a implementar**:
- `calculate_current_quantity(asset_id: int) -> Decimal`
- `calculate_average_purchase_price(asset_id: int) -> Decimal`
- `calculate_asset_value(asset_id: int, current_price: Decimal) -> Decimal`

**Testing obligatorio**:
- ✅ Test cantidad actual (compras - ventas)
- ✅ Test precio promedio ponderado
- ✅ Test valor actual del activo

---

## Task 5.3: Servicio de Desglose por Categorías

**Objetivo**: Implementar desglose de gastos e ingresos por categoría

**Archivos a crear**:
```
backend/
├── app/
│   └── services/
│       └── category_breakdown.py
```

**Funciones a implementar**:
- `get_expense_breakdown(user_id: int, start: date, end: date) -> list[dict]`
- `get_income_breakdown(user_id: int, start: date, end: date) -> list[dict]`

**Testing obligatorio**:
- ✅ Test desglose de gastos por categoría
- ✅ Test desglose de ingresos por categoría
- ✅ Test exclusión de transferencias (type='transfer')
- ✅ Test clasificación de inversiones (type='investment')

**Reglas de negocio**:
- Excluir categorías tipo 'transfer' del desglose
- Inversiones se muestran pero computan como ahorro

---

## Task 5.4: API de Dashboard

**Objetivo**: Crear endpoint para dashboard con resumen ejecutivo

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   └── dashboard.py
│   └── schemas/
│       └── dashboard.py
```

**Endpoints a implementar**:
- `GET /api/v1/dashboard/summary` - Resumen ejecutivo
- `GET /api/v1/dashboard/breakdown` - Desglose por categorías
- `GET /api/v1/dashboard/net-worth` - Patrimonio neto

**Testing obligatorio**:
- ✅ Test endpoint summary retorna datos correctos
- ✅ Test cálculo de tasa de ahorro
- ✅ Test filtros por periodo

**Response esperado de /summary**:
```json
{
  "period": {"start": "2025-01-01", "end": "2025-01-31"},
  "income": "2500.00",
  "expenses": "1200.50",
  "investments": "300.00",
  "liquid_savings": "999.50",
  "total_saved": "1299.50",
  "savings_rate": 51.98,
  "net_worth": {
    "accounts": "5000.00",
    "assets": "25000.00",
    "liabilities": "150000.00",
    "total": "-120000.00"
  }
}
```

---

## Task 5.5: Actualización Automática de Balances

**Objetivo**: Implementar hooks para actualizar balances al crear/modificar transacciones

**Archivos a modificar**:
```
backend/
├── app/
│   └── api/v1/
│       └── transactions.py
```

**Funcionalidad**:
- Al crear transacción: `account.balance += transaction.amount`
- Al actualizar transacción: revertir cambio anterior y aplicar nuevo
- Al eliminar transacción: `account.balance -= transaction.amount`

**Testing obligatorio**:
- ✅ Test balance se actualiza al crear transacción
- ✅ Test balance se actualiza correctamente al modificar
- ✅ Test balance se revierte al eliminar transacción

---

**Próxima tarea**: [06-onboarding.md](06-onboarding.md) - Implementar importación CSV y onboarding

**Nota**: Toda la lógica de negocio debe tener tests exhaustivos antes de avanzar.
