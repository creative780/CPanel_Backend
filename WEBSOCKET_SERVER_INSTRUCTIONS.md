# Starting WebSocket Server with Daphne

## Prerequisites (Already Done)
- ✅ Memurai (Redis) is running on port 6379
- ✅ Daphne is installed
- ✅ ASGI application loads successfully

## How to Start the Server

### Option 1: Using the Batch Script (Easiest)
```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"
.\start_websocket_server.bat
```

### Option 2: Manual Command
```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"
daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application
```

### Option 3: Using Python Module
```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"
python -m daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application
```

## Expected Output
When the server starts successfully, you should see:
```
2025-XX-XX XX:XX:XX [INFO] Starting server at tcp:port=8000:interface=0.0.0.0
2025-XX-XX XX:XX:XX [INFO] HTTP/2 support not enabled (install the http2 and tls Twisted extras)
2025-XX-XX XX:XX:XX [INFO] Configuring endpoint tcp:port=8000:interface=0.0.0.0
2025-XX-XX XX:XX:XX [INFO] Listening on TCP address 0.0.0.0:8000
```

## Verify WebSocket is Working

1. **Check Server Status:**
   - Open browser: http://localhost:8000/api/health/
   - Should return a health check response

2. **Check WebSocket Connection:**
   - Open browser console on the monitoring page
   - You should see: `[WebSocket] Connected successfully!`
   - Status should show "Live" instead of "Offline"

## Troubleshooting

### If Server Won't Start:
1. Check if port 8000 is already in use:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Kill any existing process on port 8000 if needed

### If WebSocket Still Shows Offline:
1. Verify Redis/Memurai is running:
   ```powershell
   python check_redis.py
   ```
2. Check browser console for WebSocket errors
3. Verify the WebSocket URL in browser console matches: `ws://localhost:8000/ws/monitoring/`

## Important Notes

- **DO NOT use `python manage.py runserver`** - it doesn't support WebSocket
- **Always use Daphne** for WebSocket support
- The server must be running for WebSocket connections to work
- Redis/Memurai must be running for Channels to work




