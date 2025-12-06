from fastapi import APIRouter, Depends, Header, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.db.models import TenantConfig
from app.schemas.tenant import TenantConfigIn, TenantConfigOut

router = APIRouter(prefix="/tenants", tags=["tenants"])

# Simple static list of tenants for demo. In production esto vendría de una tabla.
KNOWN_TENANTS = ["tenant-a", "tenant-b"]


@router.get("", response_model=List[str])
def list_tenants():
    return KNOWN_TENANTS


def require_tenant_header(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")):
    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Tenant-Id header")
    return x_tenant_id


@router.get("/{tenant_id}/config", response_model=TenantConfigOut)
def get_config(
    tenant_id: str = Path(...),
    x_tenant_id: str = Depends(require_tenant_header),
    db: Session = Depends(get_db),
):
    if x_tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this tenant")

    entry = db.query(TenantConfig).filter(TenantConfig.tenant_id == tenant_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return TenantConfigOut(tenant_id=entry.tenant_id, config=entry.config)


@router.put("/{tenant_id}/config", response_model=TenantConfigOut)
def put_config(
    tenant_id: str,
    payload: TenantConfigIn,
    x_tenant_id: str = Depends(require_tenant_header),
    db: Session = Depends(get_db),
):
    if x_tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this tenant")

    entry = db.query(TenantConfig).filter(TenantConfig.tenant_id == tenant_id).first()
    if not entry:
        entry = TenantConfig(tenant_id=tenant_id, config=payload.config)
        db.add(entry)
    else:
        entry.config = payload.config
    db.commit()
    db.refresh(entry)
    return TenantConfigOut(tenant_id=entry.tenant_id, config=entry.config)
