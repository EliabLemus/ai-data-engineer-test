FROM python:3.9-slim

# Coloque el WD dentro del paquete para que "main.py" sea importable como "main"
WORKDIR /app/sqliteapi

# Dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir fastapi "uvicorn[standard]"

# Copiar SOLO la app
COPY . /app/sqliteapi

# DB por defecto (se sobreescribe con ENV si quiere)
ENV SQLITE_DB_PATH=/app/sqliteapi/data/ADS_METRICS.sqlite

EXPOSE 8500
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8500"]
