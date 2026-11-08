FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias de FastAPI y MLflow
COPY requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt

# Copiar el codigo del proyecto
COPY mibici/ ./mibici/

# Puerto de FastAPI
EXPOSE 8000

# Iniciar el servidor FastAPI
CMD ["uvicorn", "mibici.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
