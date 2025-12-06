from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Crear tablas para los tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_tenants():
    r = client.get("/tenants")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert "tenant-a" in r.json()


def test_put_and_get_tenant_a_config():
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"theme": "dark", "language": "es"}}

    # PUT (create/update)
    r = client.put("/tenants/tenant-a/config", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "tenant-a"
    assert r.json()["config"] == payload["config"]

    # GET
    r2 = client.get("/tenants/tenant-a/config", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["config"] == payload["config"]


def test_put_tenant_b_and_get():
    headers = {"X-Tenant-Id": "tenant-b"}
    payload = {"config": {"theme": "light", "language": "en"}}

    r = client.put("/tenants/tenant-b/config", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "tenant-b"

    r2 = client.get("/tenants/tenant-b/config", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["config"] == payload["config"]


def test_missing_header_returns_400():
    r = client.get("/tenants/tenant-a/config")
    assert r.status_code == 400


def test_cross_tenant_forbidden():
    # Mismo tenant en header, distinto en la URL: prohibido
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"k": "v"}}
    r = client.put("/tenants/tenant-b/config", json=payload, headers=headers)
    assert r.status_code == 403

    r2 = client.get("/tenants/tenant-b/config", headers=headers)
    assert r2.status_code in (403, 404)
