# Backend - Fase 6: Onboarding e Importación

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 6.1: Servicio de Importación CSV - Transacciones

**Objetivo**: Implementar importación de transacciones bancarias desde CSV

**Archivos a crear**:
```
backend/
├── app/
│   └── services/
│       └── csv_importer.py
```

**Formato CSV esperado**:
```csv
fecha;concepto;importe;categoria;banco
2025-01-15;Salario mensual;2500.00;💼 Salario;Santander
2025-01-16;Compra supermercado;-85.50;🍔 Alimentos;BBVA
```

**Funcionalidad**:
- Validar formato CSV
- Crear categorías si no existen
- Crear cuentas si no existen
- Importar transacciones
- Actualizar balances de cuentas

**Testing obligatorio**:
- ✅ Test importación exitosa de CSV válido
- ✅ Test creación automática de categorías
- ✅ Test creación automática de cuentas
- ✅ Test validación de formato inválido
- ✅ Test actualización de balances

---

## Task 6.2: Servicio de Importación CSV - Activos

**Objetivo**: Implementar importación de transacciones de activos desde CSV

**Formato CSV esperado**:
```csv
fecha;activo;simbolo;cantidad;precio_unitario
2024-06-15;Bitcoin;BTC;0.5;50000.00
2025-01-10;Bitcoin;BTC;-0.2;80000.00
```

**Funcionalidad**:
- Validar formato
- Crear activos si no existen
- Calcular total_amount automáticamente
- Importar transacciones

**Testing obligatorio**:
- ✅ Test importación de compras y ventas
- ✅ Test cálculo automático de total_amount
- ✅ Test creación automática de activos

---

## Task 6.3: Servicio de Importación CSV - Pasivos

**Objetivo**: Implementar importación de transacciones de pasivos desde CSV

**Formato CSV esperado**:
```csv
fecha;pasivo;acreedor;importe
2020-01-01;Hipoteca;BBVA;150000.00
2024-12-01;Hipoteca;BBVA;-500.00
```

**Funcionalidad**:
- Validar formato
- Crear pasivos si no existen
- Importar préstamos y pagos

**Testing obligatorio**:
- ✅ Test importación de préstamos y pagos
- ✅ Test creación automática de pasivos

---

## Task 6.4: API de Onboarding

**Objetivo**: Crear endpoints para onboarding del usuario

**Archivos a crear**:
```
backend/
├── app/
│   ├── api/v1/
│   │   └── onboarding.py
│   └── schemas/
│       └── onboarding.py
```

**Endpoints**:
- `POST /api/v1/onboarding/import/transactions` - Importar CSV transacciones
- `POST /api/v1/onboarding/import/assets` - Importar CSV activos
- `POST /api/v1/onboarding/import/liabilities` - Importar CSV pasivos
- `GET /api/v1/onboarding/templates` - Descargar plantillas CSV
- `POST /api/v1/onboarding/initialize` - Inicializar con datos por defecto

**Testing obligatorio**:
- ✅ Test upload de CSV y procesamiento
- ✅ Test respuesta con resumen de importación
- ✅ Test inicialización con categorías por defecto

**Response esperado**:
```json
{
  "success": true,
  "summary": {
    "transactions_imported": 15,
    "categories_created": 3,
    "accounts_created": 2
  }
}
```

---

## Task 6.5: Inicialización de Categorías por Defecto

**Objetivo**: Crear función para inicializar categorías predeterminadas

**Funcionalidad**:
- Al registrar usuario, crear automáticamente categorías estándar
- Categorías regular: Salario, Alimentos, Transporte, Vivienda, etc.
- Categorías especiales: Transferencia, Comisión, Inversión

**Testing obligatorio**:
- ✅ Test creación de categorías por defecto al registrar usuario
- ✅ Test que incluye todas las categorías necesarias

---

**Próxima tarea**: [07-testing-integration.md](07-testing-integration.md) - Testing de integración completo

**Nota**: El sistema de importación es crítico. Tests exhaustivos obligatorios.
