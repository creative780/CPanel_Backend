# Installing FFmpeg on Backend Server

## Why FFmpeg is Required on Backend

The backend server needs FFmpeg for **server-side video encoding** (fallback when agents don't have FFmpeg). This is part of the hybrid encoding approach.

## Windows Installation

### Option 1: Download Pre-built Binary (Recommended)

1. **Download FFmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: **"ffmpeg-release-essentials.zip"**

2. **Extract FFmpeg:**
   - Extract to a folder (e.g., `C:\ffmpeg`)

3. **Add to PATH:**
   ```powershell
   # Add to system PATH permanently
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
   
   # Or add to user PATH
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "User")
   ```

4. **Restart Django/Daphne server** after adding to PATH

5. **Verify Installation:**
   ```powershell
   ffmpeg -version
   ```

### Option 2: Place in Backend Directory

If you don't want to modify PATH:

1. Download and extract FFmpeg as above
2. Copy `ffmpeg.exe` from the `bin` folder
3. Place it in: `CRM_BACKEND/` directory (same level as `manage.py`)
4. The backend will find it automatically

## Linux Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
# or
sudo dnf install ffmpeg
```

## macOS Installation

```bash
brew install ffmpeg
```

## Verify FFmpeg Works

After installation, restart the Django/Daphne server and check logs. When an agent tries server-side encoding, you should see:

```
Video encoded successfully using server-side FFmpeg: XXXXX bytes
```

Instead of:

```
ERROR FFmpeg binary not found on server. Please install FFmpeg on the backend server.
```

## Python Package

Make sure `ffmpeg-python` is installed:

```bash
cd CRM_BACKEND
pip install ffmpeg-python
```

## Quick Test

After installing, test FFmpeg from Python:

```python
import subprocess
result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
print(result.stdout)
```

## Important Notes

- **Backend must have FFmpeg**: Server-side encoding fallback requires FFmpeg on the backend
- **Restart required**: After installing FFmpeg, restart the Django/Daphne server
- **PATH vs local**: If FFmpeg is in PATH, it works system-wide. If placed in backend directory, it only works for that instance

## Troubleshooting

### "FFmpeg binary not found" after installation
- Restart the Django/Daphne server
- Verify with: `ffmpeg -version` from command line
- Check if `ffmpeg-python` package is installed: `pip list | grep ffmpeg`

### Server-side encoding still fails
- Check backend logs for specific FFmpeg errors
- Verify FFmpeg version supports H.264: `ffmpeg -codecs | grep h264`
- Ensure `ffmpeg-python` package is installed
