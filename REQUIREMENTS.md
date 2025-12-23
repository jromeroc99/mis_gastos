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

---

## Autenticación y Seguridad

### JWT (JSON Web Tokens)

**Estrategia**: Autenticación stateless con JWT para compatibilidad multi-plataforma (web + mobile).

**Flujo de autenticación**:
1. Usuario envía `email` + `password` a `/api/auth/login`
2. Backend valida credenciales contra hash bcrypt
3. Backend genera JWT firmado con claims: `user_id`, `email`, `exp` (expiración)
4. Cliente recibe `access_token` (corta duración: 15-30 min) + `refresh_token` (larga duración: 7-30 días)
5. Cliente incluye `Authorization: Bearer {access_token}` en todas las peticiones
6. Backend valida JWT en cada request con middleware
7. Cliente usa `refresh_token` en `/api/auth/refresh` para obtener nuevo `access_token`

**Endpoints de autenticación**:
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login (devuelve access_token + refresh_token)
- `POST /api/auth/refresh` - Renovar access_token con refresh_token
- `POST /api/auth/logout` - Invalidar refresh_token (opcional: blacklist)

**Configuración JWT**:
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # Variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Middleware de autenticación**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Uso en endpoints**:
```python
@router.get("/transactions")
async def list_transactions(
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # current_user contiene el user_id del token JWT
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user)
    ).all()
    return transactions
```

**Seguridad adicional**:
- Contraseñas hasheadas con bcrypt (nunca plaintext)
- HTTPS obligatorio en producción
- Rate limiting en endpoints de auth (prevenir brute force)
- CORS configurado para dominios autorizados
- Refresh tokens almacenados en httpOnly cookies (web) o secure storage (mobile)

---

## Modelo de Datos

### 0. Usuarios (Users)

**Tabla**: `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Modelo Python (SQLModel)**:
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 1. Movimientos Bancarios (Transactions)

**Tabla**: `transactions`

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    concept VARCHAR(200) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,  -- Positivo: ingreso, Negativo: gasto
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),  -- Opcional
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Regla de eliminación**: Si se elimina una cuenta, TODAS sus transacciones se eliminan en cascada. El usuario debe confirmar explícitamente esta acción destructiva.

**Modelo Python (SQLModel)**:
```python
class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: date
    concept: str = Field(max_length=200)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    account_id: int = Field(foreign_key="accounts.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 2. Categorías (Categories)

**Tabla**: `categories`

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),  -- Emoji: 💰
    color VARCHAR(7) DEFAULT '#6B7280',  -- Hex: #FF5733
    type VARCHAR(20) DEFAULT 'regular',  -- 'regular', 'transfer', 'investment'
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Tipos de Categoría**:
- `regular`: Gastos/ingresos normales que afectan el balance neto
- `transfer`: Transferencias entre cuentas (balance neto 0 - lo que sale de una entra en otra)
- `investment`: Inversión en activos (se registra como gasto pero computa como ahorro)

**Nota**: El signo del `amount` determina dirección (positivo = ingreso, negativo = gasto), pero el `type` determina cómo se contabiliza en reportes. El ahorro NO es una categoría, se calcula automáticamente como: `ingresos - gastos - inversiones`.

**Categorías Iniciales por Usuario**:

*Regular*:
- 💼 Salario
- 🎁 Regalos
- 📈 Venta de activos
- 🍔 Alimentos
- 🚗 Transporte
- 🏠 Vivienda
- 💊 Salud
- 🎮 Entretenimiento
- 📚 Educación
- 👕 Ropa
- 💳 Pagos de deudas
- 🔧 Otros

*Especiales*:
- 🔄 Transferencia (type: 'transfer') - Balance neto 0 entre cuentas*
- 💸 Comisión (type: 'regular') - Pérdida en transferencias
- 📊 Inversión (type: 'investment') - Gasto que computa como ahorro

*Si hay comisión en transferencia: 2 transacciones tipo 'transfer' + 1 transacción tipo 'regular' (comisión)

---

### 3. Cuentas (Accounts)

**Tabla**: `accounts`

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,  -- "Efectivo", "Santander", "BBVA"
    icon VARCHAR(50) DEFAULT '🏦',
    balance NUMERIC(12, 2) DEFAULT 0.00,  -- Balance actual
    currency VARCHAR(3) DEFAULT 'EUR',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Regla de negocio**: El `balance` se actualiza con cada transacción:
```python
# Al crear transacción
account.balance += transaction.amount

# Balance total del usuario
total = SUM(accounts.balance)

# Ahorro líquido: Diferencia de balances en el periodo
initial_balance = SUM(accounts.balance AT period_start)
final_balance = SUM(accounts.balance AT period_end)
liquid_savings = final_balance - initial_balance

# Ahorro total: Líquido + Inversiones
total_savings = liquid_savings + total_investments
```

**Regla de eliminación de cuenta**:
```python
async def delete_account(account_id: int) -> dict:
    """
    Eliminar cuenta CON CONFIRMACIÓN EXPLÍCITA.
    Elimina en cascada TODAS las transacciones asociadas.
    """
    account = get_account(account_id)
    transaction_count = count_transactions(account_id)
    
    # Usuario debe confirmar:
    # - Nombre de la cuenta
    # - Número de transacciones que se borrarán
    # - Balance actual
    
    confirmation = {
        'account_name': account.name,
        'transaction_count': transaction_count,
        'current_balance': account.balance,
        'warning': 'Esta acción NO se puede deshacer'
    }
    
    # Si confirma:
    session.delete(account)  # CASCADE elimina transacciones
    session.commit()
    
    return confirmation
```

---

### 4. Activos (Assets) - Catálogo

**Tabla**: `assets` - Definición de activos del usuario (similar a categorías)

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,  -- "Bitcoin", "Oro físico", "Apple Inc."
    symbol VARCHAR(20),  -- "BTC", "XAU", "AAPL"
    icon VARCHAR(50) DEFAULT '💎',
    color VARCHAR(7) DEFAULT '#10B981',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);
```

**Modelo Python**:
```python
class Asset(SQLModel, table=True):
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    symbol: Optional[str] = Field(max_length=20)
    icon: str = Field(default="💎", max_length=50)
    color: str = Field(default="#10B981", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 5. Movimientos de Activos (Asset Transactions)

**Tabla**: `asset_transactions` - Registro de compras/ventas

```sql
CREATE TABLE asset_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    date DATE NOT NULL,
    quantity NUMERIC(18, 8) NOT NULL,  -- Positivo: compra, Negativo: venta
    price_per_unit NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,  -- quantity * price_per_unit
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Regla de negocio**: El balance se calcula desde las transacciones:

```python
# Cantidad actual (compras - ventas)
current_quantity = SUM(quantity)  # Positivos + Negativos

# Precio promedio de compra
avg_purchase_price = SUM(total_amount WHERE quantity > 0) / SUM(quantity WHERE quantity > 0)
```

**Modelo Python**:
```python
class AssetTransaction(SQLModel, table=True):
    __tablename__ = "asset_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    asset_id: int = Field(foreign_key="assets.id")
    date: date
    quantity: Decimal = Field(max_digits=18, decimal_places=8)  # + compra, - venta
    price_per_unit: Decimal = Field(max_digits=12, decimal_places=2)
    total_amount: Decimal = Field(max_digits=12, decimal_places=2)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 6. Pasivos (Liabilities) - Catálogo

**Tabla**: `liabilities` - Definición de pasivos del usuario

```sql
CREATE TABLE liabilities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,  -- "Hipoteca BBVA", "Préstamo auto", "Tarjeta crédito"
    creditor VARCHAR(100),  -- "BBVA", "Santander"
    icon VARCHAR(50) DEFAULT '💳',
    color VARCHAR(7) DEFAULT '#EF4444',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);
```

**Modelo Python**:
```python
class Liability(SQLModel, table=True):
    __tablename__ = "liabilities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    creditor: Optional[str] = Field(max_length=100)
    icon: str = Field(default="💳", max_length=50)
    color: str = Field(default="#EF4444", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 7. Movimientos de Pasivos (Liability Transactions)

**Tabla**: `liability_transactions` - Registro de aumentos/pagos de deudas

```sql
CREATE TABLE liability_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    liability_id INTEGER NOT NULL REFERENCES liabilities(id),
    date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,  -- Positivo: préstamo recibido, Negativo: pago
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Regla de negocio**: El saldo de deuda actual:

```python
# Deuda actual (préstamos - pagos)
current_debt = SUM(amount)  # Positivos + Negativos
```

**Modelo Python**:
```python
class LiabilityTransaction(SQLModel, table=True):
    __tablename__ = "liability_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    liability_id: int = Field(foreign_key="liabilities.id")
    date: date
    amount: Decimal = Field(max_digits=12, decimal_places=2)  # + préstamo, - pago
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 8. Histórico Patrimonial (Net Worth History) - OPCIONAL

**Tabla**: `snapshots` - Para guardar evolución histórica

```sql
CREATE TABLE snapshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    total_accounts NUMERIC(12, 2) NOT NULL,
    total_assets NUMERIC(12, 2) NOT NULL,
    total_liabilities NUMERIC(12, 2) NOT NULL,
    net_worth NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

**Regla de negocio**: Snapshot opcional (diario/semanal/mensual):
```python
# Total activos desde asset_transactions
total_assets = 0
for asset in user_assets:
    quantity = SUM(asset_transactions.quantity WHERE asset_id=asset.id)  # + compras, - ventas
    current_price = get_current_price(asset.symbol)
    total_assets += quantity * current_price

# Total pasivos desde liability_transactions
total_liabilities = 0
for liability in user_liabilities:
    debt = SUM(liability_transactions.amount WHERE liability_id=liability.id)  # + préstamos, - pagos
    total_liabilities += debt

net_worth = SUM(accounts.balance) + total_assets - total_liabilities
```

**Nota**: Con las transacciones de activos y pasivos, el histórico completo está disponible. Los snapshots son opcionales para optimización.

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
fecha,concepto,importe,categoria,banco
2025-01-15,Salario mensual,2500.00,💼 Salario,Santander
2025-01-16,Compra supermercado,-85.50,🍔 Alimentos,BBVA
2025-01-17,Pago alquiler,-800.00,🏠 Vivienda,Santander
2025-01-18,Freelance proyecto,450.00,💼 Salario,Efectivo
```

**Formato de Plantilla CSV - Activos**:
```csv
fecha,activo,simbolo,cantidad,precio_unitario
2024-06-15,Bitcoin,BTC,0.5,50000.00
2024-08-20,Oro físico,XAU,100,60.50
2025-01-10,Bitcoin,BTC,-0.2,80000.00
```

**Formato de Plantilla CSV - Pasivos**:
```csv
fecha,pasivo,acreedor,importe
2020-01-01,Hipoteca,BBVA,150000.00
2024-12-01,Hipoteca,BBVA,-500.00
2025-01-01,Hipoteca,BBVA,-500.00
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
- [ ] No puedo eliminar activos con transacciones asociadas

**Pasivos**:
- [ ] Puedo crear pasivos (deudas) con nombre, acreedor, icono y color
- [ ] Los pasivos sirven como referencia para registrar préstamos y pagos
- [ ] Puedo editar pasivos existentes
- [ ] No puedo eliminar pasivos con transacciones asociadas

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

**Ejemplo**:
```
Mes: Enero 2025
---
Balance inicial: €2,000

Ingresos: €3,000
  💼 Salario: €2,500 (83%)
  🎁 Regalos: €500 (17%)

Gastos: €1,500
  🏠 Vivienda: €800 (53%)
  🍔 Alimentos: €400 (27%)
  🚗 Transporte: €200 (13%)
  🎮 Entretenimiento: €100 (7%)

Transferencias: €200
  🔄 Santander → BBVA: €200
  💸 Comisión transferencia: -€5 (cuenta como gasto)

Inversiones: €500 (computa como ahorro)
  📊 Inversión Bitcoin: €500

Balance final: €2,995

Ahorro líquido: €995 (€2,995 - €2,000)
Inversiones: €500

Ahorro total: €1,495 (50% de ingresos)
  - Ahorro líquido: €995 (33%)
  - Inversiones: €500 (17%)
```

---

## APIs Externas Sugeridas

### Precios de Criptomonedas
- **CoinGecko API**: https://www.coingecko.com/en/api
  - Free tier: 50 llamadas/minuto
  - Endpoint: `GET /simple/price?ids=bitcoin&vs_currencies=eur`

### Precios de Metales Preciosos
- **Metals API**: https://metals-api.com/
  - Endpoint: `GET /latest?symbols=XAU,XAG&base=EUR`

### Precios de Acciones
- **Yahoo Finance API** (via yfinance Python library)
  ```python
  import yfinance as yf
  ticker = yf.Ticker("AAPL")
  price = ticker.history(period="1d")['Close'][0]
  ```

---

## Reglas de Negocio Críticas

### Manejo de Dinero

```python
# ✅ CORRECTO
from decimal import Decimal
amount = Decimal("99.99")
```

```sql
-- ✅ CORRECTO
amount NUMERIC(12, 2) NOT NULL
```

### Clasificación de Transacciones por Tipo de Categoría

```python
def calculate_financial_summary(user_id: int, period: DateRange) -> dict:
    """Calcular resumen financiero con lógica correcta de tipos"""
    transactions = get_transactions(user_id, period)
    
    total_income = 0
    total_expenses = 0
    total_investments = 0
    transfers_out = 0
    transfers_in = 0
    
    for t in transactions:
        category = get_category(t.category_id)
        
        if category.type == 'transfer':
            # Transferencias: suma 0 (lo que sale entra)
            if t.amount < 0:
                transfers_out += abs(t.amount)
            else:
                transfers_in += t.amount
        elif category.type == 'investment':
            # Inversión: gasto que computa como ahorro
            total_investments += abs(t.amount)
        elif t.amount > 0:
            total_income += t.amount
        else:
            total_expenses += abs(t.amount)
    
    # Ahorro líquido = Diferencia de balances
    initial_balance = get_total_balance_at(user_id, period.start)
    final_balance = get_total_balance_at(user_id, period.end)
    liquid_savings = final_balance - initial_balance
    
    # Ahorro total = Líquido + Inversiones
    total_savings = liquid_savings + total_investments
    
    return {
        'income': total_income,
        'expenses': total_expenses,
        'investments': total_investments,  # Computa como ahorro
        'liquid_savings': liquid_savings,  # Diferencia de balances
        'total_saved': total_savings,  # Líquido + Inversiones
        'savings_rate': (total_savings / total_income * 100) if total_income > 0 else 0
    }
```

### Actualización de Balance

```python
def update_account_balance(account_id: int, amount: Decimal) -> Decimal:
    """Actualizar balance al crear transacción"""
    account = session.get(Account, account_id)
    account.balance += amount
    session.commit()
    return account.balance
```

### Snapshot Opcional

```python
async def create_snapshot(user_id: int) -> Snapshot:
    """Crear snapshot del patrimonio (opcional)"""
    today = date.today()
    
    # Calcular totales
    total_accounts = sum(a.balance for a in get_user_accounts(user_id))
    total_assets = sum(a.current_value for a in get_user_assets(user_id))
    total_debts = sum(d.amount for d in get_user_debts(user_id))
    
    snapshot = Snapshot(
        user_id=user_id,
        date=today,
        total_accounts=total_accounts,
        total_assets=total_assets,
        total_debts=total_debts,
        net_worth=total_accounts + total_assets - total_debts
    )
    
    session.add(snapshot)
    session.commit()
    return snapshot
```

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
