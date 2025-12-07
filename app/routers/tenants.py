from fastapi import APIRouter, Depends, Header, HTTPException, status, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.db.models import TenantConfig
from app.schemas.tenant import TenantConfigIn, TenantConfigOut
from app.metrics import record_request, record_auth_error

router = APIRouter(prefix="/tenants", tags=["tenants"])

KNOWN_TENANTS = ["tenant-a", "tenant-b"]


@router.get("", response_model=List[str])
def list_tenants(request: Request):
    # registrar la solicitud anónima
    record_request(tenant="system", method=request.method, endpoint=str(request.url.path))
    return KNOWN_TENANTS


def require_tenant_header(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")):
    if not x_tenant_id:
        # no se envió el header del tenant: registrar error de autenticación como desconocido
        record_auth_error(tenant="unknown", error_type="missing_header")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Tenant-Id header")
    return x_tenant_id


@router.get("/{tenant_id}/config", response_model=TenantConfigOut)
def get_config(
    tenant_id: str = Path(...),
    x_tenant_id: str = Depends(require_tenant_header),
    db: Session = Depends(get_db),
):
    if x_tenant_id != tenant_id:
        # intento de acceso cruzado a otro tenant: registrar error
        record_auth_error(tenant=x_tenant_id, error_type="cross_tenant_get")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this tenant")

    # buscar configuración del tenant
    entry = db.query(TenantConfig).filter(TenantConfig.tenant_id == tenant_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    # registrar solicitud exitosa
    record_request(tenant=tenant_id, method="GET", endpoint=f"/tenants/{tenant_id}/config")
    return TenantConfigOut(tenant_id=entry.tenant_id, config=entry.config)


@router.put("/{tenant_id}/config", response_model=TenantConfigOut)
def put_config(
    tenant_id: str,
    payload: TenantConfigIn,
    x_tenant_id: str = Depends(require_tenant_header),
    db: Session = Depends(get_db),
):
    if x_tenant_id != tenant_id:
        # intento de modificación cruzada a otro tenant: registrar error
        record_auth_error(tenant=x_tenant_id, error_type="cross_tenant_put")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this tenant")

    # obtener o crear la configuración del tenant
    entry = db.query(TenantConfig).filter(TenantConfig.tenant_id == tenant_id).first()
    if not entry:
        entry = TenantConfig(tenant_id=tenant_id, config=payload.config)
        db.add(entry)
    else:
        entry.config = payload.config

    db.commit()
    db.refresh(entry)

    # registrar la solicitud PUT
    record_request(tenant=tenant_id, method="PUT", endpoint=f"/tenants/{tenant_id}/config")
    return TenantConfigOut(tenant_id=entry.tenant_id, config=entry.config)
