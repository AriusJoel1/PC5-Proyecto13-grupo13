# Tenant Config Service — Sprint 1

Pequeña API en FastAPI que almacena configuraciones por tenant (multi-tenant demo).

## Requisitos
- Python 3.11
- pip

## Instalación local
1. Crear virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
## Instrucciones para ejecutar en Docker
### Construccion de Imagen

`docker build -t app-pc5:v7 .`

### Iniciar contenedor 
`docker run -p 8000:8000 --name mi-app-v7 app-pc5:v7`

### Entrar al contenedor y ejecutar tests
`docker exec -it mi-app-v7 /bin/bash`

### Correr tests
`pytest`