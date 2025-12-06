# 1. Health Check
curl -X GET http://localhost:8000/health

# 2. Listar todos los tenants disponibles
curl -X GET http://localhost:8000/tenants

# 3. Obtener configuración de un tenant (requiere header X-Tenant-Id)
curl -X GET http://localhost:8000/tenants/tenant-a/config `
  -H "X-Tenant-Id: tenant-a"

# 4. Obtener config de otro tenant
curl -X GET http://localhost:8000/tenants/tenant-b/config `
  -H "X-Tenant-Id: tenant-b"

# 5. Actualizar/Crear configuración de un tenant
curl -X PUT http://localhost:8000/tenants/tenant-a/config `
  -H "X-Tenant-Id: tenant-a" `
  -H "Content-Type: application/json" `
  -d '{"config": {"theme": "dark", "language": "es"}}'

# 6. Actualizar config de tenant-b
curl -X PUT http://localhost:8000/tenants/tenant-b/config `
  -H "X-Tenant-Id: tenant-b" `
  -H "Content-Type: application/json" `
  -d '{"config": {"theme": "light", "language": "en"}}'

# 7. Intentar acceder a config de tenant-a sin el header (debería fallar)
curl -X GET http://localhost:8000/tenants/tenant-a/config

# 8. Intentar acceder a config de tenant-a con header incorrecto (debería fallar)
curl -X GET http://localhost:8000/tenants/tenant-a/config `
  -H "X-Tenant-Id: tenant-b"