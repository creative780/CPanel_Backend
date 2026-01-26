FROM python:3.12-slim
WORKDIR /app

# Copy and install Python dependencies (using Docker-specific requirements that exclude Windows-only packages)
COPY requirements-docker.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "daphne", "-p", "8000", "-b", "0.0.0.0", "--application-close-timeout", "30", "crm_backend.asgi:application"]

