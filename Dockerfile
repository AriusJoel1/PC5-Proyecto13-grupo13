# Dockerfile
FROM python:3.11-slim

# Crear usuario no-root
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar código
COPY . /app

# Crear carpeta para la DB si se usa sqlite
RUN mkdir -p /app/data && chown -R app:app /app

USER app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
