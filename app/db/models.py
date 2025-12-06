from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func
from sqlalchemy.types import JSON
from app.db.base import Base


# El soporte nativo de SQLite para JSON depende de la versión;
# SQLAlchemy almacenará JSON como TEXT si es necesario.
class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    config = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
