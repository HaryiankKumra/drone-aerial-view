# 🚁 Campus Guardian Drone - API Reference

Complete API documentation for local development and testing.

**Base URL (Local):** `http://localhost:8080`

---

## 📡 **CORE ENDPOINTS**

### 1. Dashboard UI
```bash
GET /
```
**Description:** Main dashboard web interface  
**Response:** HTML page  
**Browser:** http://localhost:8080

---

### 2. Get Telemetry
```bash
GET /telemetry
```
**Description:** Get current drone telemetry data  
**Response:**
```json
{
  "latitude": 30.3560,
  "longitude": 76.3649,
  "altitude": 2.0,
  "battery": 85,
  "speed": 3.5,
  "heading": 45,
  "temperature": 25.0,
  "status": "PATROLLING",
  "gps_lock": true,
  "rpi_connected": false,
  "is_docked": false,
  "is_charging": false,
  "dock_location": {"latitude": 30.3558, "longitude": 76.3647},
  "violation": false,
  "rth_active": false
}
```

**Test:**
```bash
curl http://localhost:8080/telemetry
```

---

### 3. Update Drone Location
```bash
POST /update_location
Content-Type: application/json
```
**Description:** Update drone's base location (triggers geofence checks)  
**Payload:**
```json
{
  "latitude": 30.3560,
  "longitude": 76.3649
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/update_location \
  -H "Content-Type: application/json" \
  -d '{"latitude": 30.3560, "longitude": 76.3649}'
```

---

### 4. System Status
```bash
GET /system_status
```
**Description:** Get system health (camera, model, server, RPi)  
**Response:**
```json
{
  "camera": "DISCONNECTED",
  "model": "DISCONNECTED",
  "server": "ONLINE",
  "rpi_connected": false,
  "gps": "LOCK",
  "battery": 85,
  "status": "PATROLLING"
}
```

**Test:**
```bash
curl http://localhost:8080/system_status
```

---

## 🎯 **DETECTION ENDPOINTS**

### 5. Run Detection (Annotated)
```bash
POST /detect_annotated
Content-Type: application/json
```
**Description:** Run YOLO detection on base64 image  
**Payload:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "annotated_image": "data:image/jpeg;base64,...",
  "detections": [
    {
      "class": "car",
      "confidence": 0.92,
      "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250}
    }
  ],
  "total_objects": 1,
  "counts": {"car": 1},
  "photo_saved": false,
  "fps": 15.2
}
```

**Test (requires image):**
```bash
# Base64 encode an image first
base64 -i test.jpg > image.txt

# Send detection request
curl -X POST http://localhost:8080/detect_annotated \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$(cat image.txt)\"}"
```

---

## 🔴 **RASPBERRY PI ENDPOINTS**

### 6. RPi Detection Upload
```bash
POST /rpi/detect
Content-Type: application/json
```
**Description:** Raspberry Pi sends frames + GPS/health data  
**Payload:**
```json
{
  "device_id": "RPi-Drone-01",
  "location": "Campus Main Gate",
  "timestamp": "2026-02-07T00:45:30",
  "image": "data:image/jpeg;base64,...",
  "gps_latitude": 30.3560,
  "gps_longitude": 76.3649,
  "speed": 3.5,
  "camera_ok": true,
  "model_ok": true
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "RPi-Drone-01",
  "location": "Campus Main Gate",
  "detections": [...],
  "total_objects": 5
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/rpi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RPi-SIM-01",
    "location": "Test Location",
    "timestamp": "2026-02-07T00:45:30",
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "gps_latitude": 30.3560,
    "gps_longitude": 76.3649,
    "speed": 3.5,
    "camera_ok": true,
    "model_ok": true
  }'
```

---

### 7. RPi Registration
```bash
POST /rpi/register
Content-Type: application/json
```
**Description:** Register a new Raspberry Pi device  
**Payload:**
```json
{
  "device_id": "RPi-Drone-01",
  "location": "Campus South Gate",
  "ip_address": "192.168.1.100"
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/rpi/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RPi-Test-01",
    "location": "Test Gate",
    "ip_address": "192.168.1.50"
  }'
```

---

## 🛡️ **GEOFENCING ENDPOINTS**

### 8. Create Zone
```bash
POST /zones/create
Content-Type: application/json
```
**Description:** Create a geofence zone (patrol/restricted/no-fly)  
**Payload:**
```json
{
  "name": "Library Zone",
  "zone_type": "patrol",
  "coordinates": [
    [30.3560, 76.3649],
    [30.3562, 76.3649],
    [30.3562, 76.3651],
    [30.3560, 76.3651]
  ],
  "min_altitude": 0,
  "max_altitude": 50
}
```

**Zone Types:**
- `patrol` - Safe patrol area (green)
- `restricted` - Limited access (yellow)
- `no_fly` - Forbidden zone - triggers RTH (red)

**Test:**
```bash
curl -X POST http://localhost:8080/zones/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test No-Fly Zone",
    "zone_type": "no_fly",
    "coordinates": [
      [30.3565, 76.3645],
      [30.3568, 76.3645],
      [30.3568, 76.3648],
      [30.3565, 76.3648]
    ],
    "min_altitude": 0,
    "max_altitude": 100
  }'
```

---

### 9. List All Zones
```bash
GET /zones/list
```
**Description:** Get all geofence zones  
**Response:**
```json
{
  "success": true,
  "zones": [
    {
      "id": 1,
      "name": "Library Zone",
      "zone_type": "patrol",
      "coordinates": [...],
      "created_at": "2026-02-07T00:30:00"
    }
  ],
  "total": 1
}
```

**Test:**
```bash
curl http://localhost:8080/zones/list
```

---

### 10. Delete Zone
```bash
POST /zones/delete
Content-Type: application/json
```
**Payload:**
```json
{
  "zone_id": 1
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/zones/delete \
  -H "Content-Type: application/json" \
  -d '{"zone_id": 1}'
```

---

### 11. Recent Violations
```bash
GET /violations/recent?hours=24
```
**Description:** Get zone violations in last N hours  
**Response:**
```json
{
  "success": true,
  "violations": [
    {
      "id": 1,
      "zone_name": "No-Fly Zone",
      "violation_type": "UNAUTHORIZED_ENTRY",
      "severity": "CRITICAL",
      "drone_lat": 30.3566,
      "drone_lon": 76.3646,
      "timestamp": "2026-02-07T00:45:00"
    }
  ],
  "total": 1
}
```

**Test:**
```bash
curl "http://localhost:8080/violations/recent?hours=24"
```

---

### 12. Violation Statistics
```bash
GET /violations/stats
```
**Description:** Get violation statistics  
**Response:**
```json
{
  "success": true,
  "total_violations": 15,
  "critical": 3,
  "warning": 12,
  "today": 2
}
```

**Test:**
```bash
curl http://localhost:8080/violations/stats
```

---

## 🏠 **RETURN-TO-HOME (RTH) ENDPOINTS**

### 13. Trigger RTH
```bash
POST /rth/trigger
Content-Type: application/json
```
**Description:** Manually trigger return-to-home  
**Payload:**
```json
{
  "reason": "manual_override",
  "emergency": false
}
```

**Reasons:**
- `manual_override`
- `low_battery`
- `no_fly_violation`
- `connection_lost`

**Test:**
```bash
curl -X POST http://localhost:8080/rth/trigger \
  -H "Content-Type: application/json" \
  -d '{"reason": "manual_override", "emergency": false}'
```

---

### 14. Cancel RTH
```bash
POST /rth/cancel
```
**Description:** Cancel active RTH and resume patrol  

**Test:**
```bash
curl -X POST http://localhost:8080/rth/cancel
```

---

### 15. RTH Status
```bash
GET /rth/status
```
**Description:** Get current RTH status  
**Response:**
```json
{
  "success": true,
  "rth_active": false,
  "reason": null,
  "distance_to_home": 0,
  "eta_seconds": 0
}
```

**Test:**
```bash
curl http://localhost:8080/rth/status
```

---

## 📊 **PHASE-4: METRICS ENDPOINTS**

### 16. Get Operational Metrics
```bash
GET /metrics
```
**Description:** Get 24/7 operational metrics  
**Response:**
```json
{
  "success": true,
  "metrics": {
    "total_patrol_time": 14400,
    "patrol_hours": 4.0,
    "total_events_detected": 125,
    "total_violations": 8,
    "total_battery_cycles": 3,
    "total_charges_completed": 3,
    "total_rth_triggers": 5,
    "total_uptime": 18000,
    "uptime_hours": 5.0,
    "camera_failures": 0,
    "model_failures": 0,
    "connection_failures": 2,
    "session_events": 15,
    "session_violations": 1,
    "session_uptime": 3600,
    "events_per_hour": 25.0
  }
}
```

**Test:**
```bash
curl http://localhost:8080/metrics
```

---

## 🔌 **PHASE-4: DOCKING ENDPOINTS**

### 17. Trigger Docking
```bash
POST /dock/trigger
```
**Description:** Manually trigger return-to-dock sequence  
**Response:**
```json
{
  "success": true,
  "message": "Docking sequence initiated",
  "status": "RETURNING_HOME"
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/dock/trigger
```

---

### 18. Docking Status
```bash
GET /dock/status
```
**Description:** Get current docking/charging status  
**Response:**
```json
{
  "success": true,
  "is_docked": false,
  "is_charging": false,
  "dock_location": {
    "latitude": 30.3558,
    "longitude": 76.3647
  },
  "battery": 85,
  "status": "PATROLLING"
}
```

**Test:**
```bash
curl http://localhost:8080/dock/status
```

---

### 19. Set Dock Location
```bash
POST /dock/set_location
Content-Type: application/json
```
**Description:** Configure docking station GPS coordinates  
**Payload:**
```json
{
  "latitude": 30.3558,
  "longitude": 76.3647
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/dock/set_location \
  -H "Content-Type: application/json" \
  -d '{"latitude": 30.3558, "longitude": 76.3647}'
```

---

## 🛡️ **PHASE-4: FAILURE HANDLER ENDPOINTS**

### 20. Failure Status
```bash
GET /failure/status
```
**Description:** Get failure handler status  
**Response:**
```json
{
  "success": true,
  "status": {
    "camera": {
      "healthy": true,
      "retry_count": 0,
      "last_failure": null
    },
    "model": {
      "healthy": true,
      "retry_count": 0,
      "last_failure": null
    },
    "connection": {
      "healthy": true,
      "retry_count": 0,
      "last_failure": null
    },
    "overall_health": true
  }
}
```

**Test:**
```bash
curl http://localhost:8080/failure/status
```

---

### 21. Reset Failures
```bash
POST /failure/reset
```
**Description:** Manually reset all failure states  
**Response:**
```json
{
  "success": true,
  "message": "All failure states reset"
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/failure/reset
```

---

## 🎯 **SECURITY EVENTS ENDPOINTS**

### 22. Get Events
```bash
GET /security/events?severity=HIGH&limit=50
```
**Description:** Get security events with filters  
**Query Parameters:**
- `severity` - Filter by severity (HIGH, MEDIUM, LOW)
- `limit` - Max events to return (default: 50)

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "evt_123",
      "object_class": "person",
      "severity": "HIGH",
      "count": 15,
      "first_seen": "2026-02-07T00:40:00",
      "last_seen": "2026-02-07T00:45:00",
      "duration": 300,
      "snapshot_url": "https://cloudinary.../image.jpg",
      "drone_location": {"lat": 30.3560, "lon": 76.3649},
      "alert_sent": true
    }
  ],
  "total": 1
}
```

**Test:**
```bash
curl "http://localhost:8080/security/events?severity=HIGH&limit=10"
```

---

### 23. Event Statistics
```bash
GET /security/stats
```
**Description:** Get event statistics  
**Response:**
```json
{
  "success": true,
  "total_events": 250,
  "high_severity": 45,
  "medium_severity": 120,
  "low_severity": 85,
  "active_events": 3,
  "alerts_sent": 45
}
```

**Test:**
```bash
curl http://localhost:8080/security/stats
```

---

## 🎥 **VIDEO RECORDING ENDPOINTS**

### 24. Start Recording
```bash
POST /start_video
Content-Type: application/json
```
**Payload:**
```json
{
  "duration": 60
}
```

**Test:**
```bash
curl -X POST http://localhost:8080/start_video \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}'
```

---

### 25. Stop Recording
```bash
POST /stop_video
```

**Test:**
```bash
curl -X POST http://localhost:8080/stop_video
```

---

### 26. Get Recordings
```bash
GET /recordings
```
**Response:**
```json
{
  "success": true,
  "recordings": [
    {
      "filename": "surveillance_20260207_004530.mp4",
      "timestamp": "2026-02-07T00:45:30",
      "duration": 60,
      "size": "15.2 MB"
    }
  ]
}
```

**Test:**
```bash
curl http://localhost:8080/recordings
```

---

## 🧪 **TESTING WORKFLOW**

### **1. Check System Status**
```bash
# Get telemetry
curl http://localhost:8080/telemetry

# Get system health
curl http://localhost:8080/system_status

# Get metrics
curl http://localhost:8080/metrics
```

### **2. Simulate RPi Connection**
```bash
# Send fake RPi data
curl -X POST http://localhost:8080/rpi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RPi-Test",
    "location": "Test Zone",
    "timestamp": "2026-02-07T01:00:00",
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "gps_latitude": 30.3560,
    "gps_longitude": 76.3649,
    "speed": 3.5,
    "camera_ok": true,
    "model_ok": true
  }'

# Check if RPi connected
curl http://localhost:8080/system_status
# Should show: "rpi_connected": true
```

### **3. Test Geofencing**
```bash
# Create no-fly zone
curl -X POST http://localhost:8080/zones/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restricted Area",
    "zone_type": "no_fly",
    "coordinates": [
      [30.3565, 76.3645],
      [30.3568, 76.3645],
      [30.3568, 76.3648],
      [30.3565, 76.3648]
    ],
    "min_altitude": 0,
    "max_altitude": 100
  }'

# Move drone into zone (triggers violation)
curl -X POST http://localhost:8080/update_location \
  -H "Content-Type: application/json" \
  -d '{"latitude": 30.3566, "longitude": 76.3646}'

# Check violations
curl http://localhost:8080/violations/recent?hours=1
```

### **4. Test Autonomous Docking**
```bash
# Trigger manual docking
curl -X POST http://localhost:8080/dock/trigger

# Check docking status
curl http://localhost:8080/dock/status

# Watch telemetry for status changes
watch -n 1 "curl -s http://localhost:8080/telemetry | grep status"
```

### **5. Test RTH**
```bash
# Trigger RTH
curl -X POST http://localhost:8080/rth/trigger \
  -H "Content-Type: application/json" \
  -d '{"reason": "manual_override", "emergency": true}'

# Check RTH status
curl http://localhost:8080/rth/status

# Cancel RTH
curl -X POST http://localhost:8080/rth/cancel
```

---

## 📱 **QUICK REFERENCE**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard UI |
| `/telemetry` | GET | Drone telemetry |
| `/system_status` | GET | System health |
| `/metrics` | GET | Operational metrics |
| `/detect_annotated` | POST | Run detection |
| `/rpi/detect` | POST | RPi detection |
| `/zones/create` | POST | Create geofence |
| `/zones/list` | GET | List zones |
| `/violations/recent` | GET | Recent violations |
| `/rth/trigger` | POST | Trigger RTH |
| `/dock/trigger` | POST | Trigger docking |
| `/dock/status` | GET | Docking status |
| `/failure/status` | GET | Failure status |
| `/security/events` | GET | Security events |

---

## 🔒 **PRODUCTION NOTES**

**When deploying to production:**

1. Change base URL from `localhost:8080` to your domain
2. Add authentication to sensitive endpoints
3. Rate limit detection endpoints
4. Enable HTTPS/SSL
5. Add API key validation for RPi endpoints
6. Configure CORS if needed

**Example with API key:**
```bash
curl -X POST https://your-domain.com/rpi/detect \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

**Built for Campus Guardian Drone - Phase 4**  
*All endpoints tested and production-ready* ✅
