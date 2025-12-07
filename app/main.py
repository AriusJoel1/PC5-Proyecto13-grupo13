from fastapi import FastAPI, Request
from app.routers import tenants
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware
from app.metrics import metrics_response

# Crear tablas de la base de datos al iniciar la aplicación
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tenant Config Service", version="0.1.0")

# Configuración simple de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_metrics(request: Request, call_next):
    # incrementa un contador global de solicitudes
    # y evita operaciones costosas 
    response = await call_next(request)
    return response


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()


app.include_router(tenants.router)
