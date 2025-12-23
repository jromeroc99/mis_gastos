# Requirements - Mis Gastos (Control Patrimonial)

## Visión General

Aplicación backend-centric para gestión integral de patrimonio personal que permite:
- Registrar todos los movimientos bancarios (ingresos/gastos)
- Categorizar transacciones personalizadamente
- Controlar activos líquidos (cuentas bancarias)
- Gestionar activos valuables (participaciones, oro, BTC, etc.)
- Registrar pasivos (deudas, préstamos)
- Visualizar evolución histórica del patrimonio neto

**Plataformas**:
- **Fase 1**: Web App (React + Vite + Tailwind CSS)
- **Fase 2**: Mobile App (React Native / Flutter)

**Enfoque**: El backend es el componente principal con lógica de negocio completa. Los frontends son clientes ligeros que consumen la API REST.

**Documentación**:
- [Modelo de Datos](./docs/database.md) - Esquema de base de datos y reglas de negocio

---

## Autenticación y Seguridad

Ver detalles completos en [Modelo de Datos](./docs/database.md).

**Estrategia**: JWT stateless para web + mobile.

**Endpoints**:
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login (access_token + refresh_token)
- `POST /api/auth/refresh` - Renovar token
- `POST /api/auth/logout` - Cerrar sesión

---

## Historias de Usuario

### HU-000: Onboarding Inicial

**Como** nuevo usuario  
**Quiero** empezar a usar la aplicación importando mis datos históricos o desde cero  
**Para** comenzar rápidamente con mi control patrimonial

#### Criterios de Aceptación

- [ ] Al registrarme, veo una pantalla de bienvenida con dos opciones:
  - Importar datos desde CSV
  - Empezar desde cero
- [ ] Si elijo "Importar CSV", puedo descargar plantillas para:
  - **Transacciones bancarias**: `fecha`, `concepto`, `importe`, `categoria`, `banco`
  - **Activos**: `fecha`, `activo`, `simbolo`, `cantidad`, `precio_unitario`
  - **Pasivos**: `fecha`, `pasivo`, `acreedor`, `importe`
- [ ] Puedo subir uno o varios CSV y el sistema valida el formato
- [ ] Las categorías, cuentas, activos y pasivos que no existan se crean automáticamente
- [ ] Si elijo "Empezar desde cero", se crean categorías y cuentas predeterminadas
- [ ] Recibo confirmación de la importación exitosa con resumen de registros creados

**Formato de Plantilla CSV - Transacciones Bancarias**:
```csv
fecha;concepto;importe;categoria;banco
2025-01-15;Salario mensual;2500.00;💼 Salario;Santander
2025-01-16;Compra supermercado;-85.50;🍔 Alimentos;BBVA
2025-01-17;Pago alquiler;-800.00;🏠 Vivienda;Santander
2025-01-18;Freelance proyecto;450.00;💼 Salario;Efectivo
```

**Formato de Plantilla CSV - Activos**:
```csv
fecha;activo;simbolo;cantidad;precio_unitario
2024-06-15;Bitcoin;BTC;0.5;50000.00
2024-08-20;Oro físico;XAU;100;60.50
2025-01-10;Bitcoin;BTC;-0.2;80000.00
```

**Formato de Plantilla CSV - Pasivos**:
```csv
fecha;pasivo;acreedor;importe
2020-01-01;Hipoteca;BBVA;150000.00
2024-12-01;Hipoteca;BBVA;-500.00
2025-01-01;Hipoteca;BBVA;-500.00
```

**Reglas de Importación**:

*Transacciones bancarias*:
- `fecha`: Formato YYYY-MM-DD
- `importe`: Positivo para ingresos, negativo para gastos
- `categoria`: Si no existe, se crea con icono por defecto
- `banco`: Si no existe, se crea la cuenta con balance inicial 0

*Activos*:
- `fecha`: Formato YYYY-MM-DD
- `cantidad`: Positivo para compra, negativo para venta
- `activo`: Si no existe, se crea con icono por defecto 💎
- `simbolo`: Opcional (BTC, XAU, AAPL, etc.)
- El sistema calcula `total_amount = cantidad × precio_unitario`

*Pasivos*:
- `fecha`: Formato YYYY-MM-DD
- `importe`: Positivo para préstamo recibido, negativo para pago
- `pasivo`: Si no existe, se crea con icono por defecto 💳
- `acreedor`: Opcional

---

### HU-001: Registrar Movimiento Bancario

**Como** usuario  
**Quiero** registrar un ingreso o gasto en mi cuenta bancaria  
**Para** mantener actualizado el balance de mis cuentas

#### Criterios de Aceptación

- [ ] Puedo seleccionar la fecha del movimiento
- [ ] Puedo escribir el concepto (máx 200 caracteres)
- [ ] Ingreso el importe como número positivo o negativo
- [ ] Selecciono la cuenta bancaria afectada
- [ ] Selecciono o creo una categoría
- [ ] El balance de la cuenta se actualiza automáticamente
- [ ] Puedo añadir notas opcionales

---

### HU-002: Gestionar Catálogos (Categorías, Activos, Pasivos)

**Como** usuario  
**Quiero** crear y gestionar mis categorías, activos y pasivos  
**Para** organizar mis transacciones financieras

#### Criterios de Aceptación

**Categorías**:
- [ ] Puedo crear categorías con nombre, icono, color y tipo
- [ ] Tipos disponibles: regular, transfer, investment
- [ ] Las categorías pueden usarse tanto para ingresos como gastos
- [ ] El tipo determina cómo se contabiliza en reportes y desgloses
- [ ] Puedo editar y eliminar categorías personalizadas
- [ ] El ahorro NO es una categoría, es un cálculo automático

**Cuentas**:
- [ ] Puedo crear, editar y ver cuentas bancarias
- [ ] Al eliminar una cuenta, veo advertencia con: nombre, balance actual, número de transacciones
- [ ] Debo confirmar explícitamente escribiendo el nombre de la cuenta
- [ ] Al confirmar, se eliminan en cascada TODAS las transacciones asociadas
- [ ] Esta acción NO se puede deshacer

**Activos**:
- [ ] Puedo crear activos con nombre, símbolo, icono y color
- [ ] Los activos sirven como referencia para registrar transacciones de compra/venta
- [ ] Puedo editar activos existentes
- [ ] Al eliminar un activo, veo advertencia con: nombre, cantidad actual, número de transacciones
- [ ] Debo confirmar explícitamente escribiendo el nombre del activo
- [ ] Al confirmar, se eliminan en cascada TODAS las transacciones asociadas
- [ ] Esta acción NO se puede deshacer

**Pasivos**:
- [ ] Puedo crear pasivos (deudas) con nombre, acreedor, icono y color
- [ ] Los pasivos sirven como referencia para registrar préstamos y pagos
- [ ] Puedo editar pasivos existentes
- [ ] Al eliminar un pasivo, veo advertencia con: nombre, saldo pendiente, número de transacciones
- [ ] Debo confirmar explícitamente escribiendo el nombre del pasivo
- [ ] Al confirmar, se eliminan en cascada TODAS las transacciones asociadas
- [ ] Esta acción NO se puede deshacer

---

### HU-003: Registrar Movimiento de Activo

**Como** usuario  
**Quiero** registrar compras y ventas de activos (BTC, oro, acciones, etc.)  
**Para** llevar un histórico completo de mis inversiones

#### Criterios de Aceptación

- [ ] Puedo registrar compras (cantidad positiva) o ventas (cantidad negativa)
- [ ] Selecciono la fecha de la transacción
- [ ] Selecciono un activo de mi catálogo (o creo uno nuevo)
- [ ] Ingreso cantidad (+ para compra, - para venta) y precio unitario
- [ ] El sistema calcula automáticamente el total (cantidad × precio)
- [ ] Puedo ver el balance actual calculado (suma de todas las cantidades)
- [ ] Puedo ver el precio promedio de compra ponderado
- [ ] Puedo añadir notas opcionales

**Ejemplo**:
```
Activo: Bitcoin (BTC) 💰
---
Fecha: 2024-06-15 | +0.5 BTC @ €50,000 = €25,000
Fecha: 2025-01-10 | -0.2 BTC @ €80,000 = -€16,000

Balance actual: 0.3 BTC
Precio promedio compra: €50,000
Valor actual: €24,000 (a precio actual €80,000)
```

---

### HU-004: Registrar Movimiento de Pasivo

**Como** usuario  
**Quiero** registrar préstamos recibidos y pagos de deudas  
**Para** controlar mis pasivos y obligaciones financieras

#### Criterios de Aceptación

- [ ] Puedo registrar préstamos (importe positivo) o pagos (importe negativo)
- [ ] Selecciono la fecha de la transacción
- [ ] Selecciono un pasivo de mi catálogo (o creo uno nuevo)
- [ ] Ingreso el importe (+ para préstamo recibido, - para pago)
- [ ] El sistema calcula el saldo pendiente (suma de todos los importes)
- [ ] Puedo añadir notas opcionales

**Ejemplo**:
```
Pasivo: Hipoteca BBVA 🏠
---
Fecha: 2020-01-01 | +€150,000 (préstamo)
Fecha: 2024-12-01 | -€500 (pago)
Fecha: 2025-01-01 | -€500 (pago)

Saldo pendiente: €149,000
```

---

### HU-005: Visualizar Evolución Patrimonial

**Como** usuario  
**Quiero** ver un gráfico histórico de mi patrimonio neto  
**Para** analizar mi progreso financiero en el tiempo

#### Criterios de Aceptación

- [ ] Gráfico de línea con evolución mensual
- [ ] Eje Y: patrimonio neto (activos - pasivos)
- [ ] Eje X: tiempo (últimos 12 meses por defecto)
- [ ] Tooltips muestran desglose: cuentas, activos, pasivos
- [ ] Filtros: 3 meses, 6 meses, 1 año, todo

---

### HU-006: Desglose de Gastos e Ingresos

**Como** usuario  
**Quiero** ver un desglose detallado de mis gastos e ingresos por categoría  
**Para** entender en qué se va mi dinero y de dónde viene

#### Criterios de Aceptación

**Vista de Gastos**:
- [ ] Veo gráfico de pastel/dona con distribución de gastos por categoría
- [ ] Veo listado ordenado de mayor a menor gasto
- [ ] Cada categoría muestra: nombre, icono, total gastado, porcentaje del total
- [ ] Las categorías tipo 'transfer' NO se cuentan (balance neto 0)
- [ ] Las categorías tipo 'investment' se muestran como "Inversiones" y computan como ahorro
- [ ] El ahorro NO es una categoría, se calcula automáticamente
- [ ] Filtros: periodo (mes actual, últimos 3 meses, 6 meses, año, personalizado)

**Vista de Ingresos**:
- [ ] Veo gráfico de pastel/dona con distribución de ingresos por categoría
- [ ] Veo listado ordenado de mayor a menor ingreso
- [ ] Cada categoría muestra: nombre, icono, total ingresado, porcentaje del total
- [ ] Las categorías tipo 'transfer' NO se cuentan
- [ ] Mismo sistema de filtros que gastos

**Resumen Ejecutivo**:
- [ ] Total ingresos del periodo (excluyendo transferencias)
- [ ] Total gastos del periodo (solo regular, excluyendo inversiones)
- [ ] Total invertido del periodo (categoría 'investment')
- [ ] Ahorro líquido del periodo (diferencia de balances: balance_final - balance_inicial)
- [ ] Ahorro total: ahorro_líquido + inversiones
- [ ] Porcentaje de ahorro: (ahorro_total / ingresos) × 100

**Transferencias con comisión**:
- [ ] Si hay comisión, se registran 3 transacciones:
  - Transacción 1: Salida de cuenta origen (negativa, tipo 'transfer')
  - Transacción 2: Entrada a cuenta destino (positiva, tipo 'transfer')
  - Transacción 3: Comisión (negativa, tipo 'regular', categoría 💸 Comisión)
- [ ] Las transferencias (tipo 'transfer') no afectan el balance neto
- [ ] La comisión SÍ cuenta como gasto real

Ver ejemplo completo en [Modelo de Datos](./docs/database.md).

---

## Backlog Futuro

- **HU-007**: Dashboard de patrimonio con gráficos
- **HU-008**: Alertas de actualización de precios
- **HU-009**: Exportar reportes a PDF/CSV
- **HU-010**: Presupuestos por categoría
- **HU-011**: Gastos recurrentes automáticos
- **HU-012**: Multi-moneda con conversión automática

---

## Arquitectura Técnica

### Filosofía de Arquitectura

**Backend-Centric Design**: El backend contiene toda la lógica de negocio, validaciones, cálculos financieros y reglas. Los frontends (web/mobile) son clientes delgados que:
- Consumen API REST
- Manejan autenticación JWT
- Presentan datos al usuario
- Validan inputs básicos (UX)

**Beneficios**:
- Reutilización de lógica entre plataformas
- Migración fácil a mobile sin duplicar código
- Testing centralizado en backend
- Actualizaciones de lógica sin desplegar frontends

### Backend Structure (FastAPI)
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py  # Variables de entorno (SECRET_KEY, DATABASE_URL)
│   │   ├── security.py  # JWT, password hashing
│   │   └── database.py  # SQLModel engine, session
│   ├── models/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── account.py
│   │   ├── asset.py
│   │   ├── asset_transaction.py
│   │   ├── liability.py
│   │   ├── liability_transaction.py
│   │   └── snapshot.py
│   ├── schemas/
│   │   ├── auth.py  # LoginRequest, TokenResponse
│   │   ├── transaction.py  # TransactionCreate, TransactionResponse
│   │   └── ...
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py  # /login, /register, /refresh
│   │       ├── onboarding.py
│   │       ├── transactions.py
│   │       ├── categories.py
│   │       ├── accounts.py
│   │       ├── assets.py  # CRUD de activos (catálogo)
│   │       ├── asset_transactions.py  # Movimientos de activos
│   │       ├── liabilities.py  # CRUD de pasivos (catálogo)
│   │       ├── liability_transactions.py  # Movimientos de pasivos
│   │       └── dashboard.py
│   ├── services/
│   │   ├── csv_importer.py
│   │   ├── balance.py
│   │   ├── asset_calculator.py  # Calcula quantity, avg_price desde transactions
│   │   ├── prices.py
│   │   └── snapshots.py
│   ├── middleware/
│   │   ├── auth.py  # get_current_user dependency
│   │   └── cors.py  # CORS configuration
│   └── main.py
├── tests/
│   ├── test_auth.py
│   ├── test_transactions.py
│   └── ...
├── alembic/  # Database migrations
├── .env.example
├── requirements.txt
└── docker-compose.yml
```

### Frontend Structure - Web App (React + Vite + Tailwind)
```
frontend/
├── src/
│   ├── services/
│   │   ├── api.ts  # Axios instance con JWT interceptor
│   │   ├── auth.ts  # login(), register(), refreshToken()
│   │   ├── transactions.ts  # CRUD transactions
│   │   └── ...
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── transactions/
│   │   ├── accounts/
│   │   ├── assets/
│   │   ├── debts/
│   │   ├── dashboard/
│   │   └── charts/
│   ├── hooks/
│   │   ├── useAuth.ts  # Manejo de tokens, logout
│   │   ├── useTransactions.ts
│   │   ├── useAccounts.ts
│   │   ├── useAssets.ts
│   │   └── useNetWorth.ts
│   ├── context/
│   │   └── AuthContext.tsx  # Proveedor de autenticación
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
├── .env.example  # VITE_API_URL
└── package.json
```

### Frontend Structure - Mobile App (Fase 2)
```
mobile/
├── src/
│   ├── services/
│   │   ├── api.ts  # Mismo que web, con secure storage
│   │   └── auth.ts
│   ├── screens/
│   │   ├── Auth/
│   │   ├── Transactions/
│   │   ├── Dashboard/
│   │   └── ...
│   ├── components/
│   ├── hooks/
│   └── navigation/
└── package.json
```

**Nota**: La mobile app reutiliza exactamente la misma API REST que la web app, solo cambia la capa de presentación.

---

## Stack Tecnológico

### Backend (Core Application)
- **Framework**: FastAPI 0.100+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Base de Datos**: PostgreSQL 15+
- **Autenticación**: JWT (python-jose, passlib[bcrypt])
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Docker + Docker Compose

### Frontend - Web App (Fase 1)
- **Framework**: React 18+
- **Build Tool**: Vite 4+
- **Styling**: Tailwind CSS 3+
- **HTTP Client**: Axios
- **State Management**: React Context + Custom Hooks
- **Charts**: Recharts / Chart.js

### Frontend - Mobile App (Fase 2)
- **Framework**: React Native / Flutter (TBD)
- **State Management**: Same pattern as web
- **Secure Storage**: react-native-keychain / flutter_secure_storage

---

**Versión**: 2.1.0  
**Última actualización**: 2025-12-23  
**Tipo de aplicación**: Control Patrimonial Simplificado Backend-Centric  
**Plataformas**: Web App (Fase 1) → Mobile App (Fase 2)
