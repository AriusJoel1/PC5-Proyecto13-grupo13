from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Metricas
REQUESTS_BY_TENANT = Counter(
    "tenant_requests_total", "Total requests by tenant", ["tenant", "method", "endpoint"]
)
AUTH_ERRORS_BY_TENANT = Counter(
    "tenant_auth_errors_total", "Authorization errors by tenant", ["tenant", "error_type"]
)


def record_request(tenant: str, method: str, endpoint: str):
    REQUESTS_BY_TENANT.labels(tenant=tenant or "unknown", method=method, endpoint=endpoint).inc()


def record_auth_error(tenant: str, error_type: str = "forbidden"):
    AUTH_ERRORS_BY_TENANT.labels(tenant=tenant or "unknown", error_type=error_type).inc()


def metrics_response():
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
