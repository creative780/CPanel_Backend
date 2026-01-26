# Manual Testing Guide for Recording and Live Streaming System

## Prerequisites

1. Django server running: `python manage.py runserver`
2. Redis server running (for WebSocket support)
3. Agent installed and configured on a test device
4. Admin user account with proper permissions
5. FFmpeg installed (optional, for thumbnail generation)

## Part 1: Recording System Testing

### 1.1 Video Upload Test

**Steps:**
1. Start the agent on a test device
2. Ensure agent is enrolled and has a valid device token
3. Agent should automatically capture and upload video recordings
4. Check server logs for successful upload messages

**Expected Results:**
- Agent logs show "Recording sent successfully"
- No errors in server logs
- Recording appears in database

**Verification:**
```bash
# Check database for new recordings
python manage.py shell
>>> from monitoring.models import Recording
>>> Recording.objects.count()  # Should be > 0
>>> Recording.objects.last()  # Check latest recording
```

### 1.2 Admin Interface Test

**Steps:**
1. Login as admin user
2. Navigate to `/api/admin/recordings` endpoint
3. Test filtering by device: `/api/admin/recordings?device_id=<device_id>`
4. Test pagination: `/api/admin/recordings?limit=10&offset=0`
5. Verify video URLs are returned

**Expected Results:**
- API returns 200 status
- Response contains `recordings` array
- Each recording has `video_url` and `thumbnail_url`
- Recordings are ordered by `start_time` descending
- Pagination works correctly

**API Test:**
```bash
# Get admin token first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password", "role": "admin"}'

# Use token to get recordings
curl -X GET http://localhost:8000/api/admin/recordings \
  -H "Authorization: Bearer <token>"
```

### 1.3 File Serving Test

**Steps:**
1. Get a video URL from recordings API response
2. Access the video URL directly in browser: `http://localhost:8000/api/files/<blob_key>`
3. Verify video plays in browser
4. Check content-type header is `video/mp4`

**Expected Results:**
- Video file is accessible
- Browser can play the video
- Content-Type header is correct
- File downloads/serves correctly

### 1.4 Thumbnail Generation Test

**Steps:**
1. Upload a recording (agent does this automatically)
2. Check if thumbnail was generated
3. Access thumbnail URL: `http://localhost:8000/api/files/<thumb_key>`

**Expected Results:**
- Thumbnail exists (if ffmpeg is available)
- Thumbnail is a valid JPEG image
- Thumbnail displays correctly in browser

**Note:** If ffmpeg is not available, thumbnail generation will be skipped but recording will still work.

## Part 2: Live Streaming Testing

### 2.1 Agent Stream Connection Test

**Steps:**
1. Start agent on test device with live streaming enabled
2. Check agent logs for WebSocket connection messages
3. Verify connection to: `ws://<server>/ws/monitoring/stream/agent/<device_id>/?token=<device_token>`

**Expected Results:**
- Agent logs show "WebSocket connection established for live streaming"
- No connection errors
- Agent is sending frames

**Agent Logs to Check:**
```
Streaming client started
Connecting to streaming server: ws://...
WebSocket connection established for live streaming
Sent X frames to streaming server
```

### 2.2 Admin Viewer Connection Test

**Steps:**
1. Login as admin user
2. Connect to viewer WebSocket: `ws://<server>/ws/monitoring/stream/viewer/<device_id>/?token=<admin_token>`
3. Verify connection is established
4. Check if frames are being received

**Expected Results:**
- WebSocket connection successful
- Frames are received in real-time
- Frame format is JSON with base64-encoded JPEG

**WebSocket Test (using browser console or tool):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitoring/stream/viewer/<device_id>/?token=<admin_token>');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'frame') {
    console.log('Frame received:', data.timestamp);
    // Display frame: const img = document.createElement('img');
    // img.src = 'data:image/jpeg;base64,' + data.data;
  }
};
```

### 2.3 Multiple Viewers Test

**Steps:**
1. Connect first admin viewer to device stream
2. Connect second admin viewer to same device stream
3. Verify both receive frames
4. Check server performance

**Expected Results:**
- Both viewers receive frames
- No performance degradation
- Frames are synchronized (same timestamp)

### 2.4 Network Resilience Test

**Steps:**
1. Start streaming connection
2. Simulate network interruption (disconnect network briefly)
3. Reconnect network
4. Verify automatic reconnection

**Expected Results:**
- Agent automatically reconnects
- Viewer automatically reconnects
- Stream resumes without data loss (or minimal loss)

## Part 3: WebSocket Updates Testing

### 3.1 Recording Update Events

**Steps:**
1. Connect to monitoring WebSocket: `ws://<server>/ws/monitoring/?token=<admin_token>`
2. Upload a recording (via agent or API)
3. Verify `recording_update` event is received

**Expected Results:**
- Event type is `recording_update`
- Event contains device_id and recording data
- Event is received in real-time

**WebSocket Test:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitoring/?token=<admin_token>');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'recording_update') {
    console.log('Recording update:', data);
  }
};
```

### 3.2 Device-Specific Recording Events

**Steps:**
1. Connect to device-specific WebSocket: `ws://<server>/ws/monitoring/device/<device_id>/?token=<admin_token>`
2. Upload a recording for that device
3. Verify `device_recording` event is received

**Expected Results:**
- Event type is `device_recording`
- Event contains recording data
- Only events for that device are received

## Part 4: Integration Testing

### 4.1 End-to-End Recording Flow

**Steps:**
1. Agent captures video segment
2. Agent uploads to `/api/ingest/recording`
3. Server stores video and creates Recording record
4. Admin views recording via `/api/admin/recordings`
5. Admin plays video via `/api/files/<blob_key>`

**Expected Results:**
- All steps complete successfully
- Video is playable
- Recording metadata is correct
- No errors in any step

### 4.2 Live Streaming Flow

**Steps:**
1. Agent starts streaming frames
2. Agent connects to WebSocket stream endpoint
3. Admin connects to viewer WebSocket endpoint
4. Admin receives and displays frames in real-time

**Expected Results:**
- Stream is established
- Frames are received in real-time
- Latency is acceptable (< 2 seconds)
- Stream quality is good

## Troubleshooting

### Recording Issues

**Problem:** Recordings not appearing in admin panel
- Check device token is valid
- Verify recording was actually uploaded (check server logs)
- Check database for Recording records
- Verify API endpoint is correct

**Problem:** Video files not accessible
- Check file serving endpoint is working
- Verify blob_key is correct
- Check file exists in storage location
- Verify content-type headers

### Streaming Issues

**Problem:** Agent cannot connect to stream
- Verify WebSocket URL is correct
- Check device token is valid
- Verify Redis is running (for channel layers)
- Check server logs for connection errors

**Problem:** Viewers not receiving frames
- Verify agent is connected and sending frames
- Check WebSocket connection is established
- Verify channel layer is working
- Check browser console for errors

**Problem:** High latency
- Reduce frame rate in agent
- Check network bandwidth
- Verify server performance
- Consider reducing frame quality

## Test Checklist

### Recording System
- [ ] Video upload works
- [ ] Recordings appear in admin API
- [ ] Video files are accessible
- [ ] Thumbnails are generated (if ffmpeg available)
- [ ] Pagination works
- [ ] Filtering by device works
- [ ] User snapshots are captured
- [ ] Idle period recordings work

### Live Streaming
- [ ] Agent connects to stream
- [ ] Admin viewer connects
- [ ] Frames are received
- [ ] Multiple viewers work
- [ ] Reconnection works
- [ ] Stream quality is acceptable

### WebSocket Updates
- [ ] Recording update events fire
- [ ] Device recording events fire
- [ ] Events are received in real-time
- [ ] Event data is correct

## Performance Benchmarks

### Recording System
- Upload time: < 5 seconds for 1-minute video
- API response time: < 500ms
- File serving: < 100ms for small files

### Live Streaming
- Connection time: < 2 seconds
- Frame latency: < 2 seconds
- Frame rate: 5-10 FPS
- Bandwidth: ~500KB/s per stream


