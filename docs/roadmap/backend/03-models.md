# Backend - Fase 3: Modelos de Datos Principales

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## Task 3.1: Implementar Modelos de Categorías y Cuentas

**Objetivo**: Crear modelos para Categories y Accounts con reglas de negocio

**Archivos a crear**:
```
backend/
├── app/
│   └── models/
│       ├── category.py
│       └── account.py
```

**Contenido de `app/models/category.py`**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: str = Field(default="#6B7280", max_length=7)
    type: str = Field(default="regular", max_length=20)  # regular, transfer, investment
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Contenido de `app/models/account.py`**:
```python
from sqlmodel import SQLModel, Field, Numeric
from datetime import datetime
from typing import Optional
from decimal import Decimal

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    icon: str = Field(default="🏦", max_length=50)
    balance: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2, sa_type=Numeric(12, 2))
    currency: str = Field(default="EUR", max_length=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Actualizar `app/models/__init__.py`**:
```python
from .user import User
from .category import Category
from .account import Account

__all__ = ["User", "Category", "Account"]
```

**Actualizar `app/core/database.py`**:
```python
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from .config import settings

# Importar todos los modelos
from app.models import User, Category, Account  # noqa

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

**Testing**:
```python
# tests/test_category_account_models.py
import pytest
from decimal import Decimal
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.user import User
from app.models.category import Category
from app.models.account import Account
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    create_db_and_tables()
    yield

@pytest.fixture
def test_user(session: Session):
    """Crear usuario de prueba"""
    user = User(
        email="[email protected]",
        password_hash=get_password_hash("password"),
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_category(test_user):
    """Test crear categoría"""
    with Session(engine) as session:
        category = Category(
            user_id=test_user.id,
            name="Alimentos",
            icon="🍔",
            color="#FF5733",
            type="regular"
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Alimentos"
        assert category.type == "regular"

def test_create_account(test_user):
    """Test crear cuenta"""
    with Session(engine) as session:
        account = Account(
            user_id=test_user.id,
            name="Santander",
            icon="🏦",
            balance=Decimal("1000.50"),
            currency="EUR"
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        
        assert account.id is not None
        assert account.balance == Decimal("1000.50")
        assert isinstance(account.balance, Decimal)

def test_account_default_balance(test_user):
    """Test que el balance por defecto es 0.00"""
    with Session(engine) as session:
        account = Account(
            user_id=test_user.id,
            name="BBVA"
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        
        assert account.balance == Decimal("0.00")
```

**Comandos de verificación**:
```bash
docker-compose down -v && docker-compose up -d
pytest tests/test_category_account_models.py -v
```

**Criterio de aceptación**:
- ✅ Modelos Category y Account creados
- ✅ Balance usa Decimal correctamente
- ✅ Tipos de categoría (regular, transfer, investment) soportados
- ✅ Tests pasan correctamente

---

## Task 3.2: Implementar Modelo de Transacciones

**Objetivo**: Crear modelo Transaction con validación de tipos Decimal

**Archivos a crear**:
```
backend/
├── app/
│   └── models/
│       └── transaction.py
```

**Contenido de `app/models/transaction.py`**:
```python
from sqlmodel import SQLModel, Field, Numeric
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: date
    concept: str = Field(max_length=200)
    amount: Decimal = Field(max_digits=12, decimal_places=2, sa_type=Numeric(12, 2))
    account_id: int = Field(foreign_key="accounts.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Actualizar `app/models/__init__.py`**:
```python
from .user import User
from .category import Category
from .account import Account
from .transaction import Transaction

__all__ = ["User", "Category", "Account", "Transaction"]
```

**Actualizar `app/core/database.py`**:
```python
from app.models import User, Category, Account, Transaction  # noqa
```

**Testing**:
```python
# tests/test_transaction_model.py
import pytest
from decimal import Decimal
from datetime import date
from sqlmodel import Session
from app.core.database import engine, create_db_and_tables
from app.models import User, Category, Account, Transaction
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup():
    create_db_and_tables()

@pytest.fixture
def test_data():
    """Preparar datos de prueba"""
    with Session(engine) as session:
        user = User(
            email="[email protected]",
            password_hash=get_password_hash("pass"),
            name="Test"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        category = Category(
            user_id=user.id,
            name="Salario",
            icon="💼"
        )
        session.add(category)
        
        account = Account(
            user_id=user.id,
            name="Santander",
            balance=Decimal("0.00")
        )
        session.add(account)
        session.commit()
        session.refresh(category)
        session.refresh(account)
        
        return user, category, account

def test_create_transaction(test_data):
    """Test crear transacción"""
    user, category, account = test_data
    
    with Session(engine) as session:
        transaction = Transaction(
            user_id=user.id,
            date=date(2025, 1, 15),
            concept="Salario mensual",
            amount=Decimal("2500.00"),
            account_id=account.id,
            category_id=category.id
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.id is not None
        assert transaction.amount == Decimal("2500.00")
        assert isinstance(transaction.amount, Decimal)
        assert transaction.date == date(2025, 1, 15)

def test_transaction_negative_amount(test_data):
    """Test transacción con monto negativo (gasto)"""
    user, category, account = test_data
    
    with Session(engine) as session:
        transaction = Transaction(
            user_id=user.id,
            date=date.today(),
            concept="Compra supermercado",
            amount=Decimal("-85.50"),
            account_id=account.id,
            category_id=category.id
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.amount == Decimal("-85.50")
        assert transaction.amount < 0
```

**Comandos de verificación**:
```bash
docker-compose down -v && docker-compose up -d
pytest tests/test_transaction_model.py -v
```

**Criterio de aceptación**:
- ✅ Modelo Transaction creado
- ✅ Campo amount usa Decimal con precisión correcta
- ✅ Fechas usan tipo DATE (sin hora)
- ✅ Tests con montos positivos y negativos pasan

---

## Task 3.3: Implementar Modelos de Activos

**Objetivo**: Crear modelos Asset y AssetTransaction

**Archivos a crear**:
```
backend/
├── app/
│   └── models/
│       ├── asset.py
│       └── asset_transaction.py
```

**Contenido de `app/models/asset.py`**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Asset(SQLModel, table=True):
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    symbol: Optional[str] = Field(default=None, max_length=20)
    icon: str = Field(default="💎", max_length=50)
    color: str = Field(default="#10B981", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Contenido de `app/models/asset_transaction.py`**:
```python
from sqlmodel import SQLModel, Field, Numeric
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class AssetTransaction(SQLModel, table=True):
    __tablename__ = "asset_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    asset_id: int = Field(foreign_key="assets.id")
    date: date
    quantity: Decimal = Field(max_digits=18, decimal_places=8, sa_type=Numeric(18, 8))
    price_per_unit: Decimal = Field(max_digits=12, decimal_places=2, sa_type=Numeric(12, 2))
    total_amount: Decimal = Field(max_digits=12, decimal_places=2, sa_type=Numeric(12, 2))
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Actualizar imports en `app/models/__init__.py`** y `app/core/database.py`

**Testing**:
```python
# tests/test_asset_models.py
import pytest
from decimal import Decimal
from datetime import date
from sqlmodel import Session
from app.core.database import engine, create_db_and_tables
from app.models import User, Asset, AssetTransaction
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup():
    create_db_and_tables()

@pytest.fixture
def test_user():
    with Session(engine) as session:
        user = User(
            email="[email protected]",
            password_hash=get_password_hash("pass"),
            name="Test"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def test_create_asset(test_user):
    """Test crear activo"""
    with Session(engine) as session:
        asset = Asset(
            user_id=test_user.id,
            name="Bitcoin",
            symbol="BTC",
            icon="₿"
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        assert asset.id is not None
        assert asset.symbol == "BTC"

def test_create_asset_transaction(test_user):
    """Test crear transacción de activo"""
    with Session(engine) as session:
        # Crear activo
        asset = Asset(
            user_id=test_user.id,
            name="Bitcoin",
            symbol="BTC"
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        # Compra (cantidad positiva)
        transaction = AssetTransaction(
            user_id=test_user.id,
            asset_id=asset.id,
            date=date(2024, 6, 15),
            quantity=Decimal("0.5"),
            price_per_unit=Decimal("50000.00"),
            total_amount=Decimal("25000.00")
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.quantity == Decimal("0.5")
        assert transaction.total_amount == Decimal("25000.00")
        assert isinstance(transaction.quantity, Decimal)
```

**Comandos de verificación**:
```bash
docker-compose down -v && docker-compose up -d
pytest tests/test_asset_models.py -v
```

**Criterio de aceptación**:
- ✅ Modelos Asset y AssetTransaction creados
- ✅ Quantity usa Decimal(18, 8) para precisión
- ✅ Tests pasan correctamente

---

## Task 3.4: Implementar Modelos de Pasivos

**Objetivo**: Crear modelos Liability y LiabilityTransaction

**Archivos a crear**:
```
backend/
├── app/
│   └── models/
│       ├── liability.py
│       └── liability_transaction.py
```

**Contenido de `app/models/liability.py`**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Liability(SQLModel, table=True):
    __tablename__ = "liabilities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    creditor: Optional[str] = Field(default=None, max_length=100)
    icon: str = Field(default="💳", max_length=50)
    color: str = Field(default="#EF4444", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Contenido de `app/models/liability_transaction.py`**:
```python
from sqlmodel import SQLModel, Field, Numeric
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class LiabilityTransaction(SQLModel, table=True):
    __tablename__ = "liability_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    liability_id: int = Field(foreign_key="liabilities.id")
    date: date
    amount: Decimal = Field(max_digits=12, decimal_places=2, sa_type=Numeric(12, 2))
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Actualizar imports**

**Testing**:
```python
# tests/test_liability_models.py
import pytest
from decimal import Decimal
from datetime import date
from sqlmodel import Session
from app.core.database import engine, create_db_and_tables
from app.models import User, Liability, LiabilityTransaction
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup():
    create_db_and_tables()

@pytest.fixture
def test_user():
    with Session(engine) as session:
        user = User(
            email="[email protected]",
            password_hash=get_password_hash("pass"),
            name="Test"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def test_create_liability(test_user):
    """Test crear pasivo"""
    with Session(engine) as session:
        liability = Liability(
            user_id=test_user.id,
            name="Hipoteca BBVA",
            creditor="BBVA",
            icon="🏠"
        )
        session.add(liability)
        session.commit()
        session.refresh(liability)
        
        assert liability.id is not None
        assert liability.creditor == "BBVA"

def test_create_liability_transaction(test_user):
    """Test transacción de pasivo"""
    with Session(engine) as session:
        liability = Liability(
            user_id=test_user.id,
            name="Hipoteca",
            creditor="BBVA"
        )
        session.add(liability)
        session.commit()
        session.refresh(liability)
        
        # Préstamo recibido (positivo)
        transaction = LiabilityTransaction(
            user_id=test_user.id,
            liability_id=liability.id,
            date=date(2020, 1, 1),
            amount=Decimal("150000.00")
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        assert transaction.amount == Decimal("150000.00")
```

**Comandos de verificación**:
```bash
docker-compose down -v && docker-compose up -d
pytest tests/test_liability_models.py -v
```

**Criterio de aceptación**:
- ✅ Modelos Liability y LiabilityTransaction creados
- ✅ Campos usan Decimal correctamente
- ✅ Tests pasan correctamente

---

**Próxima tarea**: [04-apis-crud.md](04-apis-crud.md) - Implementar APIs CRUD para todos los modelos

**Nota**: NO avanzar hasta que todos los modelos estén creados y testeados correctamente.
