# Proyecto 13 — Servicio Multi-Tenant con FastAPI + SQLAlchemy + Docker + Métricas

Este proyecto implementa un **servicio multi-tenant** para administrar configuraciones por tenant.  
Cada tenant accede únicamente a su propia configuración usando el header `X-Tenant-Id`.

El proyecto incluye:


### Correr tests
`pytest`
- API REST con **FastAPI 0.99**
- Base de datos **SQLite** (dev) y **Postgres** (docker-compose)
- Multi-tenant auth por header
- Métricas **Prometheus** por tenant
- Dockerfile multi-stage endurecido
- Docker Compose (API + DB)
- Scripts de carga / seeds
- CI/CD con workflow para **SBOM + Security Scan**
- Tests automatizados con Pytest

---

#  Estructura de Carpetas
PC5-prueba/
│
├── app/
│ ├── core/config.py
│ ├── db/
│ │ ├── base.py
│ │ ├── models.py
│ │ └── session.py
│ ├── routers/
│ │ └── tenants.py
│ ├── schemas/
│ │ └── tenant.py
│ ├── metrics.py
│ └── main.py
│
├── scripts/
│ ├── init_db.py
│ └── load_by_tenant.py
│
├── tests/
│ └── test_app.py
│
├── data/ (generado en runtime)
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md


---

## Funcionalidad Principal

### Multi-Tenant
Cada petición debe incluir:


Si el tenant no coincide con la URL (`/tenants/tenant-a/...`), responde **403 Forbidden**.

---

### Endpoints principales

| Método | Ruta | Descripción |
|-------|-------|-------------|
| `GET` | `/health` | Estado del servicio |
| `GET` | `/tenants` | Lista de tenants disponibles |
| `GET` | `/tenants/{tenant_id}/config` | Obtiene configuración del tenant |
| `PUT` | `/tenants/{tenant_id}/config` | Actualiza configuración del tenant |
| `GET` | `/metrics` | Métricas Prometheus |

---

## Métricas Prometheus (Sprint 2)

Incluye contadores por tenant:

Estas métricas permiten medir:

- Cantidad de tráfico por tenant  
- Intentos inválidos o maliciosos  
- Operaciones GET/PUT por recurso  

---

#  Tests (Pytest)

Ejecutar:

```powershell
pytest -q
```

- Health check
- GET/PUT válido por tenant
- Acceso cruzado rechazado
- Validación de headers
- Persistencia en Base de Datos

### Base de Datos
Modo desarrollo (local):
SQLite usando archivo:
sqlite:///./data/data.db

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
python scripts/load_by_tenant.py --tenant tenant-a --n 30 --delay 0.1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/metrics"
docker build -t tenant-config-service .
docker run -p 8000:8000 tenant-config-service
docker compose up --build
$env:DATABASE_URL="postgresql://dev:dev@db:5432/tenant_config_db"
docker compose up --build
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tenants/tenant-a/config" -Headers @{ "X-Tenant-Id" = "tenant-a" }
$body = @{ config = @{ msg="hola docker" } } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tenants/tenant-a/config" -Method PUT -ContentType "application/json" -Headers @{ "X-Tenant-Id" = "tenant-a" } -Body $body
```

# Sprint 3

# 1. iniciar minikube con driver docker
minikube start --driver=docker

# 2. Aplicar namespaces
kubectl apply -f manifests/namespaces.yaml

# 3. Crear ServiceAccounts
kubectl apply -f manifests/serviceaccount-and-rolebindings.yaml

# 4. Crear Roles y RoleBindings para tenant-a
kubectl apply -f manifests/role-tenant.yaml
kubectl apply -f manifests/rolebinding-tenant.yaml

# (Si quieres tenant-b)
# edit manifests/role-tenant.yaml -> namespace tenant-b and apply
# edit manifests/rolebinding-tenant.yaml -> namespace tenant-b and subject tenant-b-sa
# or use yq/sed to patch for tenant-b:
kubectl apply -f manifests/role-tenant.yaml -n tenant-b || true
kubectl apply -f manifests/rolebinding-tenant.yaml -n tenant-b || true

# 5. Deploy API in platform namespace
kubectl apply -f manifests/deployment-service.yaml

# 6. Verificar recursos
kubectl get ns
kubectl get deployments -n platform
kubectl get pods -n platform
kubectl get roles --all-namespaces
kubectl get rolebindings --all-namespaces

# 7. Pruebas RBAC (simulate calls)
kubectl auth can-i get configmaps --as system:serviceaccount:tenant-a:tenant-a-sa -n tenant-a
kubectl auth can-i get configmaps --as system:serviceaccount:tenant-a:tenant-a-sa -n tenant-b

# 8. Ejecutar Conftest / OPA locally (requiere conftest instalado or docker)
docker run --rm -v "${PWD}":/workspace instrumenta/conftest test /workspace/manifests --policy /workspace/policy || true

# 9. Recolectar evidencias
bash scripts/collect_evidence.sh

# 10. Revisar .evidence/
ls -la .evidence
