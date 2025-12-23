# Backend - Fase 4: APIs CRUD

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 4.1: API CRUD de Categorías

**Objetivo**: Implementar endpoints completos para gestión de categorías

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   └── categories.py
│   └── schemas/
│       └── category.py
```

**Testing obligatorio**:
- ✅ GET /api/v1/categories - Listar categorías del usuario
- ✅ POST /api/v1/categories - Crear categoría
- ✅ GET /api/v1/categories/{id} - Obtener una categoría
- ✅ PUT /api/v1/categories/{id} - Actualizar categoría
- ✅ DELETE /api/v1/categories/{id} - Eliminar categoría

**Reglas de negocio**:
- Solo el usuario propietario puede acceder a sus categorías
- Validar tipos: regular, transfer, investment
- Al crear usuario, crear categorías predeterminadas

---

## Task 4.2: API CRUD de Cuentas

**Objetivo**: Implementar endpoints para gestión de cuentas bancarias

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   └── accounts.py
│   └── schemas/
│       └── account.py
```

**Testing obligatorio**:
- ✅ GET /api/v1/accounts - Listar cuentas
- ✅ POST /api/v1/accounts - Crear cuenta
- ✅ PUT /api/v1/accounts/{id} - Actualizar cuenta
- ✅ DELETE /api/v1/accounts/{id} - Eliminar con confirmación

**Reglas de negocio**:
- Validación: Al eliminar cuenta, mostrar advertencia (nombre, balance, # transacciones)
- Eliminación en cascada de transacciones
- Balance se actualiza desde transacciones

---

## Task 4.3: API CRUD de Transacciones

**Objetivo**: Implementar endpoints para movimientos bancarios

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   └── transactions.py
│   └── schemas/
│       └── transaction.py
```

**Testing obligatorio**:
- ✅ GET /api/v1/transactions - Listar con filtros (fecha, cuenta, categoría)
- ✅ POST /api/v1/transactions - Crear transacción
- ✅ GET /api/v1/transactions/{id} - Obtener transacción
- ✅ PUT /api/v1/transactions/{id} - Actualizar transacción
- ✅ DELETE /api/v1/transactions/{id} - Eliminar transacción

**Reglas de negocio**:
- Al crear/actualizar transacción, actualizar balance de cuenta
- Validar que cuenta pertenece al usuario
- Validar que fecha es DATE (sin hora)
- Monto debe ser Decimal

---

## Task 4.4: API CRUD de Activos

**Objetivo**: Implementar endpoints para catálogo y transacciones de activos

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   ├── assets.py
│   │   └── asset_transactions.py
│   └── schemas/
│       ├── asset.py
│       └── asset_transaction.py
```

**Testing obligatorio**:
- ✅ CRUD completo de assets (catálogo)
- ✅ CRUD completo de asset_transactions
- ✅ GET /api/v1/assets/{id}/summary - Balance y precio promedio

**Reglas de negocio**:
- Calcular balance actual: SUM(quantity)
- Calcular precio promedio ponderado de compra
- Al eliminar asset, advertencia con # transacciones

---

## Task 4.5: API CRUD de Pasivos

**Objetivo**: Implementar endpoints para catálogo y transacciones de pasivos

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   ├── liabilities.py
│   │   └── liability_transactions.py
│   └── schemas/
│       ├── liability.py
│       └── liability_transaction.py
```

**Testing obligatorio**:
- ✅ CRUD completo de liabilities (catálogo)
- ✅ CRUD completo de liability_transactions
- ✅ GET /api/v1/liabilities/{id}/summary - Saldo pendiente

**Reglas de negocio**:
- Calcular saldo pendiente: SUM(amount)
- Validar: positivo = préstamo, negativo = pago
- Al eliminar liability, advertencia con # transacciones

---

**Próxima tarea**: [05-business-logic.md](05-business-logic.md) - Implementar lógica de negocio y cálculos financieros

**Nota**: Todas las APIs deben tener tests completos antes de avanzar.
