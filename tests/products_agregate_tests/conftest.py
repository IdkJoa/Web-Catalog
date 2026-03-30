"""
conftest.py — Fixtures compartidos para todos los tests.

Estrategia:
- SQLite en memoria compartida (URI con cache=shared) para que el engine
  del products_agregate_tests y el engine de la app usen la misma base de datos.
- Se parchea app.db.db_connection con el engine y SessionLocal de products_agregate_tests
  ANTES de importar main, de modo que cada request de FastAPI use la
  misma sesión que los fixtures.
- Override de get_current_active_user para simular auth.
"""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# ── Variables de entorno mínimas para que Settings no falle ──────────────────
import os
os.environ.update({
    "SECRET_KEY": "products_agregate_tests-secret-key",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
    "EMAIL_TOKEN_EXPIRE_HOURS": "24",
    "RESET_PASSWORD_TOKEN_EXPIRE_MINUTES": "15",
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "587",
    "SMTP_USER": "products_agregate_tests@products_agregate_tests.com",
    "SMTP_PASSWORD": "testpassword",
    "EMAILS_FROM": "products_agregate_tests@products_agregate_tests.com",
    "FRONTEND_URL": "http://localhost:3000",
    "db_connection_url": "sqlite:///:memory:",
})

# ── Engine de products_agregate_tests (SQLite en memoria, misma conexión compartida) ─────────────
SQLITE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Parchear el módulo de conexión ANTES de importar main ────────────────────
import app.db.db_connection as _db_mod
_db_mod.engine = engine
_db_mod.SessionLocal = TestingSessionLocal

from app.models.models import Base, Category, Brand, Condition, Warranty, Product, Capacity
from app.db.db_connection import get_db
from app.core.security import get_current_active_user
from main import app


# ── Setup / teardown de tablas por cada products_agregate_tests ──────────────────────────────────
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ── Sesión de DB de products_agregate_tests ──────────────────────────────────────────────────────
@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ── Clientes HTTP ─────────────────────────────────────────────────────────────
@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    mock_user = MagicMock()
    mock_user.is_active = True
    mock_user.is_confirmed = True
    mock_user.id = uuid.uuid4()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


# ── Fixtures de datos ─────────────────────────────────────────────────────────
@pytest.fixture
def category(db) -> Category:
    obj = Category(
        id=uuid.uuid4(),
        name="Laptops",
        slug="laptops",
        description="Categoría de laptops de alta gama y oficina",
        image_url="http://example.com/images/laptops.png",
        sort_order=1,
        is_active=True,
        meta_title="Laptops y Computadoras Portátiles",
        meta_description="Compra las mejores laptops con garantía extendida.",
        meta_keywords="laptops, portatiles, gaming, oficina"
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture
def brand(db) -> Brand:
    obj = Brand(
        id=uuid.uuid4(),
        name="Dell",
        slug="dell",
        is_active=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture
def condition(db) -> Condition:
    obj = Condition(
        id=uuid.uuid4(),
        name="Nuevo",
        description="Producto nuevo",
        sort_order=1,
        is_active=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture
def warranty(db) -> Warranty:
    obj = Warranty(
        id=uuid.uuid4(),
        duration="12 meses",
        is_active=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture
def product(db, category, brand, condition, warranty) -> Product:
    obj = Product(
        id=uuid.uuid4(),
        category_id=category.id,
        brand_id=brand.id,
        condition_id=condition.id,
        warranty_id=warranty.id,
        name="Dell XPS 15",
        model_name="XPS-15-2024",
        price=1500.00,
        sale_price=1300.00,
        stock_status=True,
        is_featured=False,
        is_active=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture
def product_payload(category, brand, condition, warranty) -> dict:
    return {
        "category_id": str(category.id),
        "brand_id": str(brand.id),
        "condition_id": str(condition.id),
        "warranty_id": str(warranty.id),
        "name": "MacBook Pro",
        "model_name": "MBP-M3-2024",
        "price": "2000.0000",
        "sale_price": "1800.0000",
        "stock_status": True,
        "is_featured": False,
        "is_active": True,
        "image_url": None,
    }