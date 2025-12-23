# Modelo de Datos - Mis Gastos

## 0. Usuarios (Users)

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

## 1. Movimientos Bancarios (Transactions)

**Tabla**: `transactions`

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date DATE NOT NULL,  -- Solo fecha, sin hora (lo que importa es el día)
    concept VARCHAR(200) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,  -- Positivo: ingreso, Negativo: gasto
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),  -- Opcional
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()  -- Auditoría del sistema
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

## 2. Categorías (Categories)

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

## 3. Cuentas (Accounts)

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

**Regla de eliminación de activo**:
```python
async def delete_asset(asset_id: int) -> dict:
    """
    Eliminar activo CON CONFIRMACIÓN EXPLÍCITA.
    Elimina en cascada TODAS las transacciones asociadas.
    """
    asset = get_asset(asset_id)
    transaction_count = count_asset_transactions(asset_id)
    current_quantity = calculate_current_quantity(asset_id)
    
    # Usuario debe confirmar:
    # - Nombre del activo
    # - Número de transacciones que se borrarán
    # - Cantidad actual
    
    confirmation = {
        'asset_name': asset.name,
        'transaction_count': transaction_count,
        'current_quantity': current_quantity,
        'warning': 'Esta acción NO se puede deshacer'
    }
    
    # Si confirma:
    session.delete(asset)  # CASCADE elimina transacciones
    session.commit()
    
    return confirmation
```

**Regla de eliminación de pasivo**:
```python
async def delete_liability(liability_id: int) -> dict:
    """
    Eliminar pasivo CON CONFIRMACIÓN EXPLÍCITA.
    Elimina en cascada TODAS las transacciones asociadas.
    """
    liability = get_liability(liability_id)
    transaction_count = count_liability_transactions(liability_id)
    current_debt = calculate_current_debt(liability_id)
    
    # Usuario debe confirmar:
    # - Nombre del pasivo
    # - Número de transacciones que se borrarán
    # - Saldo pendiente
    
    confirmation = {
        'liability_name': liability.name,
        'transaction_count': transaction_count,
        'current_debt': current_debt,
        'warning': 'Esta acción NO se puede deshacer'
    }
    
    # Si confirma:
    session.delete(liability)  # CASCADE elimina transacciones
    session.commit()
    
    return confirmation
```

---

## 4. Activos (Assets) - Catálogo

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

## 5. Movimientos de Activos (Asset Transactions)

**Tabla**: `asset_transactions` - Registro de compras/ventas

```sql
CREATE TABLE asset_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    date DATE NOT NULL,  -- Solo fecha, sin hora
    quantity NUMERIC(18, 8) NOT NULL,  -- Positivo: compra, Negativo: venta
    price_per_unit NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,  -- quantity * price_per_unit
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()  -- Auditoría del sistema
);
```

**Regla de eliminación**: Si se elimina un activo, TODAS sus transacciones se eliminan en cascada. El usuario debe confirmar explícitamente esta acción destructiva.

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

## 6. Pasivos (Liabilities) - Catálogo

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

## 7. Movimientos de Pasivos (Liability Transactions)

**Tabla**: `liability_transactions` - Registro de aumentos/pagos de deudas

```sql
CREATE TABLE liability_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    liability_id INTEGER NOT NULL REFERENCES liabilities(id) ON DELETE CASCADE,
    date DATE NOT NULL,  -- Solo fecha, sin hora
    amount NUMERIC(12, 2) NOT NULL,  -- Positivo: préstamo recibido, Negativo: pago
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()  -- Auditoría del sistema
);
```

**Regla de eliminación**: Si se elimina un pasivo, TODAS sus transacciones se eliminan en cascada. El usuario debe confirmar explícitamente esta acción destructiva.

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

## 8. Histórico Patrimonial (Net Worth History) - OPCIONAL

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
