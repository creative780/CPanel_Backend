#!/usr/bin/env python
"""
Check if Redis is available and provide installation instructions if not.
"""
import sys
import subprocess

def check_redis_connection():
    """Check if Redis is accessible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=1, socket_connect_timeout=2)
        r.ping()
        print("[OK] Redis is running and accessible!")
        print(f"   Host: localhost:6379")
        print(f"   Database: 1")
        return True
    except ImportError:
        print("[ERROR] Redis Python client is not installed")
        print("   Run: pip install redis")
        return False
    except (redis.ConnectionError, redis.TimeoutError, TimeoutError, ConnectionError):
        print("[ERROR] Redis is not running or not accessible")
        print("   Connection to localhost:6379 failed")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking Redis: {e}")
        return False

def check_daphne():
    """Check if Daphne is installed"""
    try:
        import daphne
        print("[OK] Daphne is installed!")
        return True
    except ImportError:
        print("[ERROR] Daphne is not installed")
        print("   Run: pip install daphne")
        return False

def print_installation_instructions():
    """Print installation instructions for Windows"""
    print("\n" + "="*60)
    print("INSTALLATION INSTRUCTIONS FOR WINDOWS")
    print("="*60)
    print("\nOption 1: Install Memurai (Recommended - Easiest)")
    print("  1. Download from: https://www.memurai.com/get-memurai")
    print("  2. Run the installer")
    print("  3. Memurai will start automatically as a Windows service")
    print("  4. Verify: redis-cli ping (should return PONG)")
    print("\nOption 2: Use WSL (Windows Subsystem for Linux)")
    print("  1. Open WSL: wsl")
    print("  2. Install Redis: sudo apt install redis-server")
    print("  3. Start Redis: sudo service redis-server start")
    print("\nOption 3: Use Docker Desktop")
    print("  1. Install Docker Desktop for Windows")
    print("  2. Run: docker run -d -p 6379:6379 redis:7-alpine")
    print("\nFor more details, see: REDIS_SETUP_WINDOWS.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("Checking WebSocket prerequisites...\n")
    
    redis_ok = check_redis_connection()
    daphne_ok = check_daphne()
    
    print()
    
    if redis_ok and daphne_ok:
        print("[OK] All prerequisites are met!")
        print("\nYou can start the server with WebSocket support:")
        print("   daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application")
        print("   OR")
        print("   .\\start_websocket_server.bat")
        sys.exit(0)
    else:
        print("[WARNING] Some prerequisites are missing.")
        print_installation_instructions()
        
        if not redis_ok:
            print("\n[IMPORTANT] Redis is required for WebSocket support.")
            print("   Without Redis, WebSocket connections will fail.")
        
        sys.exit(1)

