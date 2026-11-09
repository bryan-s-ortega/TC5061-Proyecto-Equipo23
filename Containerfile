FROM python:3.13-slim

# Instalar uv desde la imagen oficial de Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Configuración de variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    MODEL_PATH="/app/models/p2_champion"

# Copiar archivos de dependencias y lockfile estricto de uv
COPY pyproject.toml uv.lock ./

# Instalar dependencias exactas del proyecto usando uv.lock (sin dependencias de dev)
RUN uv sync --frozen --no-dev --no-install-project

# Copiar el código del proyecto y el modelo empaquetado
COPY mibici/ ./mibici/
COPY models/ ./models/
COPY README.md LICENSE ./

# Instalar el paquete mibici en el entorno virtual de producción
RUN uv sync --frozen --no-dev

# Exponer el puerto de FastAPI
EXPOSE 8000

# Iniciar el servidor FastAPI con Uvicorn
CMD ["uvicorn", "mibici.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
