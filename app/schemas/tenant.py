from pydantic import BaseModel
from typing import Any, Dict


class TenantConfigIn(BaseModel):
    config: Dict[str, Any]


class TenantConfigOut(BaseModel):
    tenant_id: str
    config: Dict[str, Any]

    class Config:
        orm_mode = True
