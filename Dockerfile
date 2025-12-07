
# Stage 1: Builder

FROM python:3.11-slim AS builder

# Directorio de trabajo
WORKDIR /app

# Instalar herramientas necesarias para compilar paquetes Python (solo aquí)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y generar wheels (paquetes precompilados)
COPY requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r /app/requirements.txt

# Stage 2: Runtime

FROM python:3.11-slim

# Crear usuario no-root
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Copiar requirements para que pip pueda resolver dependencias
COPY requirements.txt /app/requirements.txt

# Copiar wheels generados desde el builder
COPY --from=builder /app/wheels /wheels

# Instalar dependencias desde wheels (rápido y sin necesidad de compilación)
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /app/requirements.txt

# Copiar el código de la aplicación
COPY . /app

# Crear carpeta para la base de datos (si usas SQLite)
RUN mkdir -p /app/data && chown -R app:app /app

# Cambiar a usuario no-root
USER app

# Exponer puerto para FastAPI/Uvicorn
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
