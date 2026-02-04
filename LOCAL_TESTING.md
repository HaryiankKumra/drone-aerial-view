# 🧪 Local Testing Guide

## Quick Start

### Method 1: Using Start Script (Easiest)

```bash
cd '/Users/mohitkumra/Desktop/DL Notebooks/hack'
./start.sh
```

### Method 2: Manual Start

```bash
cd '/Users/mohitkumra/Desktop/DL Notebooks/hack'

# Load environment variables
export CLOUDINARY_API_SECRET='CjTNupJulkSZmSv7vaknaogJD1A'

# Start app
.venv/bin/python app.py
```

Then open: http://localhost:8080

---

## Environment Variables

Your `.env` file is already configured with:

```env
CLOUDINARY_CLOUD_NAME=dq9v0bo36
CLOUDINARY_API_KEY=895472581156914
CLOUDINARY_API_SECRET=CjTNupJulkSZmSv7vaknaogJD1A
```

**These are YOUR credentials** - already working!

---

## Testing Checklist

### 1. Start Detection ✓
- Click "Start Detection" button
- Allow camera access
- You should see live feed

### 2. Test Object Detection ✓
- Hold up an image/object in front of camera
- Green boxes should appear around detected objects
- Alerts panel shows detections

### 3. Test Snapshot Recording ✓
- Click "Record" button while detecting
- Check logs: "✓ Snapshot saved to storage"
- Check Cloudinary: Should see uploaded image

### 4. Test Video Recording ✓
- Click "Start Recording" button
- Record for 10-15 seconds
- Click "Stop Recording"
- Check logs for:
  - "✓ Video saved! XX.XX MB"
  - "☁️ Uploaded to cloud: ..."
  - CSV file uploaded

### 5. Test CSV Logging ✓
- While detecting, CSV is being written in real-time
- Location: `recordings/logs/events_YYYYMMDD_HHMMSS.csv`
- Download: http://localhost:8080/download_csv
- Open in Excel to see all events

### 6. Verify Cloudinary Uploads ✓

**Images**: https://console.cloudinary.com/console/c-dq9v0bo36/media_library/folders/campus-guardian/detections

**Videos**: https://console.cloudinary.com/console/c-dq9v0bo36/media_library/folders/campus-guardian/videos

**CSV Logs**: https://console.cloudinary.com/console/c-dq9v0bo36/media_library/folders/campus-guardian/logs

---

## Expected Behavior

### Dashboard Display:
- ✅ Green boxes on live feed
- ✅ Real-time FPS counter
- ✅ Detection alerts
- ✅ Object count statistics

### Saved Videos:
- ✅ NO green boxes (raw footage)
- ✅ Clean, professional recording
- ✅ Uploaded to Cloudinary

### CSV Log Format:
```csv
Timestamp,Date,Time,Event_Type,Object_Class,Count,Confidence,Alert_Level,Location_X,Location_Y,Notes
2026-02-04 23:41:52.825,2026-02-04,23:41:52,VEHICLE_DETECTED,car,1,0.91,WARNING,150,200,1 car detected
```

---

## Troubleshooting

### Camera Not Working?
```bash
# Check camera permissions in System Settings
# macOS: System Settings → Privacy & Security → Camera
```

### Port 8080 Already in Use?
```bash
lsof -ti:8080 | xargs kill -9
```

### Cloudinary Not Uploading?
```bash
# Check environment variable is set
echo $CLOUDINARY_API_SECRET

# Should output: CjTNupJulkSZmSv7vaknaogJD1A
```

### CSV Not Generating?
```bash
# Check if directory exists
ls -la recordings/logs/

# Should see: events_YYYYMMDD_HHMMSS.csv
```

---

## File Locations

### Local Storage:
- **CSV Logs**: `recordings/logs/events_*.csv`
- **Videos**: `recordings/events/recording_*.mp4`
- **Snapshots**: `recordings/events/event_*.jpg`

### Cloudinary Storage:
- **Images**: `campus-guardian/detections/`
- **Videos**: `campus-guardian/videos/`
- **CSV**: `campus-guardian/logs/`

---

## API Endpoints for Testing

### Health Check:
```bash
curl http://localhost:8080/health
```

### Download CSV:
```
http://localhost:8080/download_csv
```

### CSV Status:
```bash
curl http://localhost:8080/csv_status
```

### Recording Status:
```bash
curl http://localhost:8080/recording_status
```

---

## Performance Tips

### For Best Detection:
- Good lighting
- Objects clearly visible
- Camera stable
- Top-down angle (aerial view works best)

### Reduce Notifications:
- 30-second cooldown prevents duplicate alerts
- Same object won't alert twice within 30s
- But STILL logged to CSV every frame

---

## Stop Application

Press `CTRL+C` in terminal

Or:
```bash
lsof -ti:8080 | xargs kill -9
```

---

## Next: Deploy to Render

After local testing is successful:

1. Push to GitHub (already done ✓)
2. Set environment variable on Render:
   - Key: `CLOUDINARY_API_SECRET`
   - Value: `CjTNupJulkSZmSv7vaknaogJD1A`
3. Render auto-deploys
4. Live at: https://drone-aerial-view.onrender.com/

---

## Need Help?

Check the logs in terminal for any errors or status messages:
- ✅ Green messages = Success
- ⚠️ Yellow messages = Warnings
- ❌ Red messages = Errors
