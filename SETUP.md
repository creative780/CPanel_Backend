# Backend Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env` if not already done
   - Update `.env` with your configuration (optional for development)

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the development server on port 9000:**
   ```bash
   python manage.py runserver 127.0.0.1:9000
   ```

   **Important:** The frontend expects the backend to run on port 9000 by default. 
   If you need to use a different port, update `NEXT_PUBLIC_API_BASE_URL` in the frontend `.env.local` file.

5. **Verify the server is running:**
   - Open http://127.0.0.1:9000/api/ in your browser
   - You should see the API root or a response from Django REST Framework

## Environment Variables

See `.env.example` for all available environment variables.

### Key Variables:

- **SECRET_KEY**: Django secret key (required for production)
- **DEBUG**: Set to `True` for development, `False` for production
- **FRONTEND_KEY**: Optional authentication key that must match `NEXT_PUBLIC_FRONTEND_KEY` in frontend
- **Database variables**: Optional - defaults to SQLite if not provided

## Troubleshooting

### Port Already in Use

If port 9000 is already in use:

1. **Option 1:** Stop the process using port 9000
   ```bash
   # Windows
   netstat -ano | findstr :9000
   taskkill /PID <PID> /F
   ```

2. **Option 2:** Run on a different port and update frontend `.env.local`
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
   Then update `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` in frontend `.env.local`

### Connection Refused Errors

If the frontend shows `ERR_CONNECTION_REFUSED`:
- Verify the backend server is running
- Check that the port matches `NEXT_PUBLIC_API_BASE_URL` in frontend `.env.local`
- Ensure the backend is bound to `127.0.0.1` (not just `localhost`)

## Production

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Set a secure `SECRET_KEY`
3. Configure proper database settings
4. Set `FRONTEND_KEY` for API security
5. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn backend.wsgi:application --bind 127.0.0.1:9000 --config gunicorn.conf.py
   ```

