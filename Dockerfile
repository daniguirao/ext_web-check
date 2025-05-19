FROM python:3.11-slim

WORKDIR /app

# Instalamos herramientas de compilación mínimas necesarias para netifaces
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev && \
    rm -rf /var/lib/apt/lists/*

# Creamos el directorio de tests
RUN mkdir -p /tests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY tests.py /tests/

CMD ["python", "app.py"]
