FROM python:3.12-slim

# Dependências do sistema para PyMuPDF e WeasyPrint (Debian Bookworm)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgl1 \
    libcairo2 \
    libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    fontconfig fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Não inclui .env no container — variáveis injetadas pelo Render
ENV PYTHONUNBUFFERED=1
ENV OAUTHLIB_INSECURE_TRANSPORT=0
ENV OAUTHLIB_RELAX_TOKEN_SCOPE=1

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "gthread", "--threads", "4", "--timeout", "180"]
