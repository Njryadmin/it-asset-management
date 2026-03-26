FROM python:3.11-slim

WORKDIR /app
RUN mkdir -p /app/static /app/static/icons

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy app
COPY . .

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--workers", "2"]
