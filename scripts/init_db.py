"""
Script para inicializar la BD con ejemplos
"""
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.models import TenantConfig


def init():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Insertar config ejemplo
    existing = db.query(TenantConfig).filter_by(tenant_id="tenant-a").first()
    if not existing:
        print("Insertando ejemplo para tenant-a")
        entry = TenantConfig(tenant_id="tenant-a", config={"welcome": "hello tenant A"})
        db.add(entry)
    existing_b = db.query(TenantConfig).filter_by(tenant_id="tenant-b").first()
    if not existing_b:
        print("Insertando ejemplo para tenant-b")
        entryb = TenantConfig(tenant_id="tenant-b", config={"welcome": "hello tenant B"})
        db.add(entryb)
    db.commit()
    db.close()
    print("Hecho.")


if __name__ == "__main__":
    init()
