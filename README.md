# CRM Backend (Django 5 + DRF)

Quick start

1. Create venv and install deps
   - Windows PowerShell:
     - `py -m venv .venv`
     - `./.venv/Scripts/python -m pip install -U pip`
     - `./.venv/Scripts/python -m pip install -r requirements.txt`
2. Environment
   - Copy `.env.example` to `.env` and edit as needed
3. Migrate & seed
   - `./.venv/Scripts/python Backend/manage.py migrate`
   - `./.venv/Scripts/python Backend/manage.py seed_demo`
4. Run
   - **IMPORTANT**: Use Daphne (ASGI server) instead of runserver for proper WebSocket and async support
   - Windows: `start_daphne.bat` or `python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application`
   - Linux/Mac: `./start_daphne.sh` or `python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application`
   - See `ASGI_SERVER_SETUP.md` for detailed instructions

Core endpoints

- Auth:
  - POST /api/auth/login
  - POST /api/auth/register (admin)
  - GET /api/auth/me
- Monitoring:
  - GET /api/employees
  - POST /api/track
  - POST /api/screenshot
  - POST /api/screenshot/delete
- Orders:
  - POST /api/orders
  - PATCH /api/orders/{id}
  - POST /api/orders/{id}/actions/mark-printed
  - POST /api/decrement-inventory (legacy)
- Delivery:
  - POST /api/delivery/send-code
  - POST /api/send-delivery-code (legacy)
  - POST /api/delivery/rider-photo
  - POST /api/upload-rider-photo (legacy)
- Inventory:
  - GET /api/inventory/items
  - POST /api/inventory/adjust (admin)
- HR:
  - GET /api/hr/employees
  - POST /api/hr/salary-slips

Docs

- OpenAPI schema: /api/schema/
- Swagger UI: /api/docs/
- Health: /healthz

Activity Logs Service

- App: `activity_log`
- Endpoints:
  - POST `/api/activity-logs/ingest` (HMAC)
  - GET `/api/activity-logs/` (cursor pagination; JWT)
  - GET `/api/activity-logs/{id}` (JWT)
  - POST `/api/activity-logs/export` (JWT, async)
  - GET `/api/activity-logs/exports/{job_id}` (JWT)
  - GET `/api/activity-logs/metrics` (JWT)

Docker Compose (web, db, redis, celery, celery-beat)

```
docker compose -f Backend/docker-compose.yml up --build
```

Environment

- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `CORS_ALLOWED_ORIGINS`

SDK

- Python client at `Backend/activity_log/clients/python/activity_logs_client.py`

Chat Service

- App: Matrix (Synapse)
- Real-time chat using Matrix protocol
- Matrix homeserver: Synapse (configured in docker-compose.yml)
- Frontend: Uses matrix-js-sdk with useMatrixChat hook
- Backend: Matrix user sync via accounts service
- Endpoints:
  - GET `/api/auth/matrix-config/` (get Matrix configuration for authenticated user)
  - GET `/api/chat/users/` (list users available for chat - used for Matrix user mapping)
- Matrix Admin API: User creation and management via accounts.matrix_service
- Features: Real-time messaging, typing indicators, read receipts, file attachments via Matrix protocol
- Features: typing indicators, read receipts, attachments, markdown rendering
- Bot service: Echo bot (default), OpenAI/Groq integration ready
- Frontend: Enhanced ChatBot component with real-time features