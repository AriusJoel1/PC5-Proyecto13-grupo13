from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Configurar DB en memoria para tests
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

# Crear tablas
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_put_get_same_tenant():
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"k": "v"}}
    # put
    r = client.put("/tenants/tenant-a/config", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "tenant-a"
    assert r.json()["config"] == payload["config"]

    # get
    r2 = client.get("/tenants/tenant-a/config", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["config"] == payload["config"]


def test_cross_tenant_forbidden():
    # Put: enviamos la solicitud como si fuéramos "tenant-a"
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"hello": "world"}}
    r = client.put("/tenants/tenant-b/config", json=payload, headers=headers)
    assert r.status_code == 403

    # También probamos que tampoco pueda LEER la configuración de otro tenant
    r2 = client.get("/tenants/tenant-b/config", headers=headers)
    assert r2.status_code in (403, 404)  # acceso prohibido o no existe (si el tenant-b no tiene config creada)
