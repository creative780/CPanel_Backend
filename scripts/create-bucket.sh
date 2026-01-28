#!/bin/bash

# Create MinIO bucket for web-to-print app
echo "Creating MinIO bucket..."

# Wait for MinIO to be ready
until curl -f http://localhost:9000/minio/health/live; do
  echo "Waiting for MinIO to be ready..."
  sleep 2
done

# Configure MinIO client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create bucket
mc mb local/web-to-print --ignore-existing

echo "MinIO bucket created successfully!"