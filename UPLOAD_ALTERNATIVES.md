# Alternative Methods to Upload Large .exe Files

## Problem
SCP is timing out/resetting when uploading 192MB files. This is common with large files over SSH.

## Solutions (Choose One)

### Option 1: Use WinSCP (Recommended - Most Reliable)

1. **Download WinSCP**: https://winscp.net/eng/download.php
2. **Connect**:
   - Host: `31.97.191.155`
   - Username: `root`
   - Password: (your server password)
   - Protocol: SFTP
3. **Upload files**:
   - Navigate to: `/home/api.crm.click2print.store/public_html/media/agents/`
   - Drag and drop `crm-monitoring-agent-windows-amd64.exe`
   - Also upload to: `/home/api.crm.click2print.store/public_html/media/uploads/agents/`

**Benefits**: Resume capability, progress bar, more reliable for large files

### Option 2: Use FileZilla (Free Alternative)

1. **Download FileZilla**: https://filezilla-project.org/
2. **Connect**:
   - Host: `sftp://31.97.191.155`
   - Username: `root`
   - Password: (your server password)
   - Port: `22`
3. **Upload files** to the same directories as above

### Option 3: Use rsync (If Available)

If you have rsync installed (or can install it):

```powershell
# Install rsync for Windows (via WSL or Git Bash)
# Or use WSL: wsl rsync -avz --progress "media/agents/crm-monitoring-agent-windows-amd64.exe" root@31.97.191.155:/home/api.crm.click2print.store/public_html/media/agents/
```

### Option 4: Use CyberPanel File Manager

1. **Access CyberPanel**: https://31.97.191.155:8090
2. **Login** with your admin credentials
3. **Go to File Manager**
4. **Navigate to**: `/home/api.crm.click2print.store/public_html/media/agents/`
5. **Upload** the .exe files via web interface

### Option 5: Split File and Upload in Chunks

If the file is too large, you can split it:

```powershell
# Split file into 50MB chunks
Split-File -Path "media/agents/crm-monitoring-agent-windows-amd64.exe" -ChunkSize 50MB

# Upload each chunk
scp "media/agents/crm-monitoring-agent-windows-amd64.exe.part1" root@31.97.191.155:/tmp/
scp "media/agents/crm-monitoring-agent-windows-amd64.exe.part2" root@31.97.191.155:/tmp/
# ... etc

# On server, combine chunks:
# cat /tmp/crm-monitoring-agent-windows-amd64.exe.part* > /home/api.crm.click2print.store/public_html/media/agents/crm-monitoring-agent-windows-amd64.exe
```

### Option 6: Increase SSH Timeout and Retry

Try with increased timeouts:

```powershell
scp -o StrictHostKeyChecking=accept-new `
    -o ServerAliveInterval=30 `
    -o ServerAliveCountMax=10 `
    -o TCPKeepAlive=yes `
    -C `
    "media/agents/crm-monitoring-agent-windows-amd64.exe" `
    root@31.97.191.155:/home/api.crm.click2print.store/public_html/media/agents/
```

## Recommended: WinSCP

For 192MB files, **WinSCP is the most reliable** because:
- ✅ Resume capability if connection drops
- ✅ Progress bar shows real-time status
- ✅ Better error handling
- ✅ Can queue multiple files
- ✅ Free and easy to use

## After Upload

Once files are on the server, verify:

```bash
# On server
ls -lh /home/api.crm.click2print.store/public_html/media/agents/*.exe
ls -lh /home/api.crm.click2print.store/public_html/media/uploads/agents/*.exe
```

Files should be accessible via Django at:
- `https://api.crm.click2print.store/media/agents/crm-monitoring-agent-windows-amd64.exe`
- `https://api.crm.click2print.store/media/uploads/agents/crm-monitoring-agent-windows-amd64.exe`
