# 🚁 Campus Guardian Drone - PHASE 4 DEPLOYMENT GUIDE

**Production-Ready Autonomous Campus Security System**  
*Hackathon Demo & Real-World Deployment*

---

## 🎯 **DEPLOYMENT OVERVIEW**

This is a **deployment-ready** system designed to answer the judges' question:  
**"Can this run 24/7 in production?"**

**Answer: YES.**

### **Phase 4 Features**
✅ **Autonomous Docking & Charging** - Self-returns at <20% battery  
✅ **Auto-Resume Patrol** - Continues at ≥90% charged  
✅ **Failure Recovery** - Camera/model/connection auto-retry  
✅ **Operational Metrics** - Track patrol time, events, violations, battery cycles  
✅ **RPi Integration** - Use real GPS/speed data when available  
✅ **Dockerized** - One-command deployment  

---

## 📋 **SYSTEM REQUIREMENTS**

### **Hardware (Production)**
- Server: 4GB RAM, 2 CPU cores minimum
- GPU: Optional (YOLO runs on CPU but faster with GPU)
- Raspberry Pi 4B+ (for real drone integration)
- USB Camera or IP Camera (for live detection)

### **Hardware (Demo/Simulation)**
- Laptop: 8GB RAM (runs backend simulation)
- Webcam: Any laptop camera (browser-based detection)
- No drone required for hackathon demo

### **Software**
- Docker & Docker Compose **OR**
- Python 3.11+ with pip

---

## 🚀 **QUICK START (DOCKER - RECOMMENDED)**

### **1. Clone & Setup**
```bash
git clone <your-repo-url>
cd hack

# Copy environment template
cp .env.example .env
```

### **2. Configure Environment**
Edit `.env` file:
```env
# REQUIRED: Cloudinary (for image storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# OPTIONAL: Telegram alerts
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# OPTIONAL: Weather data
OPENWEATHER_API_KEY=your_api_key
```

### **3. Build & Run**
```bash
# Build the Docker image
docker-compose build

# Start the system
docker-compose up -d

# Check logs
docker-compose logs -f guardian-drone
```

### **4. Access Dashboard**
Open browser: **http://localhost:8080**

### **5. Stop System**
```bash
docker-compose down
```

---

## 🛠️ **MANUAL INSTALLATION (WITHOUT DOCKER)**

### **1. Install Dependencies**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python packages
pip install -r requirements-deploy.txt
```

### **2. Setup Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### **3. Run Server**
```bash
source .venv/bin/activate
python app.py
```

Server starts at: **http://localhost:8080**

---

## 🔧 **CONFIGURATION GUIDE**

### **Docking Station Setup**

The system auto-configures a docking station near the initial drone position. To customize:

**Method 1: Frontend (Map)**
1. Open dashboard → Expand map
2. Drag drone to patrol start location
3. Docking station auto-positions nearby

**Method 2: API**
```bash
curl -X POST http://localhost:8080/dock/set_location \
  -H "Content-Type: application/json" \
  -d '{"latitude": 30.3560, "longitude": 76.3649}'
```

### **Autonomous Behavior Configuration**

Edit `backend/telemetry/drone_state.py`:
```python
# Battery thresholds
LOW_BATTERY_THRESHOLD = 20  # Auto-RTH trigger (%)
FULL_CHARGE_THRESHOLD = 90  # Auto-resume patrol (%)

# Charging rate
charging_rate = 5.0  # Percent per 10 seconds

# Patrol pattern
patrol_pattern = "diamond"  # or "circular"
patrol_radius = 0.0018  # ~200 meters
```

### **Failure Handler Configuration**

Edit `backend/failure_handler.py`:
```python
CAMERA_RETRY_INTERVAL = 5   # seconds
MODEL_RETRY_INTERVAL = 10   # seconds
CONNECTION_RETRY_INTERVAL = 3  # seconds
MAX_RETRIES = 3  # before manual intervention
```

---

## 🎭 **DEMO MODE (HACKATHON)**

### **For Judges - No Hardware Required**

**What Runs:**
- ✅ Backend server (simulates drone telemetry)
- ✅ YOLOv8 detection (webcam feed)
- ✅ Autonomous loop (battery drain → RTH → charge → resume)
- ✅ Geofencing & violations
- ✅ Event detection & alerts
- ✅ Metrics tracking

**What's Simulated:**
- GPS position (diamond patrol pattern around browser location)
- Battery drain (realistic decay over time)
- Docking & charging (logical simulation)
- Speed & altitude (patrol simulation)

**Demo Script:**
1. **Start System**: `docker-compose up -d`
2. **Open Dashboard**: http://localhost:8080
3. **Allow Camera Access**: Click "START DETECTION"
4. **Show Live Detection**: Point camera at people/vehicles
5. **Show Autonomous Loop**:
   - Open browser console → `fetch('/telemetry').then(r=>r.json()).then(console.log)`
   - Show battery draining
   - Create violation → Triggers RTH
   - Battery <20% → Auto-RTH
   - Watch charging (+5% every 10s)
   - Battery ≥90% → Auto-resume
6. **Show Metrics Panel**: 24/7 operational data
7. **Show Geofencing**: Create zones, trigger violations
8. **Show Events Log**: 5-second persistence rule

---

## 🔌 **RASPBERRY PI INTEGRATION (PRODUCTION)**

### **Hardware Setup**

**RPi Components:**
- Raspberry Pi 4B (4GB+)
- Official RPi Camera Module V2
- GPS Module (optional - can use phone GPS)
- 4G/LTE USB Dongle (for remote operation)

### **RPi Software Installation**

```bash
# On Raspberry Pi
git clone <repo-url>
cd hack

# Install dependencies
pip install opencv-python requests pillow

# Configure
nano rpi_config.json
```

**rpi_config.json:**
```json
{
  "server_url": "http://your-server-ip:8080",
  "device_id": "RPi-Drone-01",
  "location": "Campus Main Gate",
  "send_interval": 3,
  "camera_index": 0
}
```

### **Start RPi Client**

```bash
# Run detection client
python raspberry_pi/rpi_detection_client.py
```

**What RPi Sends:**
- Video frames (3-second intervals)
- GPS coordinates (if GPS module connected)
- Speed data (calculated from GPS)
- Camera health status
- Model status

**What Server Does:**
- Runs YOLO detection on RPi frames
- Uses RPi GPS data for real position
- Uses RPi speed for telemetry
- Tracks RPi connection (10s timeout)
- Falls back to laptop location if RPi disconnects

---

## 📊 **OPERATIONAL METRICS**

### **Tracked Metrics (24/7)**
- **Total Patrol Time**: Hours of active patrolling
- **Total Events**: Object detections logged
- **Total Violations**: Zone breaches
- **Battery Cycles**: Complete charge cycles
- **RTH Triggers**: Emergency returns
- **Total Uptime**: System operational time
- **Failure Counts**: Camera/model/connection issues

### **API Endpoints**

**Get Metrics:**
```bash
curl http://localhost:8080/metrics
```

**Get Failure Status:**
```bash
curl http://localhost:8080/failure/status
```

**Trigger Docking:**
```bash
curl -X POST http://localhost:8080/dock/trigger
```

**Reset Failures:**
```bash
curl -X POST http://localhost:8080/failure/reset
```

---

## 🚨 **FAILURE RECOVERY**

### **Automatic Recovery**

**Camera Failure:**
- Retry every 5 seconds
- Max 3 attempts
- Logs to metrics
- UI shows "DISCONNECTED"

**Model Failure:**
- Retry every 10 seconds
- Reloads YOLO model
- Max 3 attempts
- Falls back to safe mode

**Connection Failure (RPi):**
- Retry every 3 seconds
- Falls back to laptop GPS
- Speed = 0 when disconnected
- Continues patrol in degraded mode

### **Manual Recovery**

**Reset All Failures:**
```bash
curl -X POST http://localhost:8080/failure/reset
```

**Or via UI:**
- Dashboard → System Health → Click "Reset Failures"

---

## 🧪 **TESTING THE 24/7 LOOP**

### **Test Autonomous Charging**

**Method 1: API (Fast Test)**
```bash
# Force low battery
curl -X POST http://localhost:8080/update_battery \
  -H "Content-Type: application/json" \
  -d '{"battery": 15}'

# Watch in browser console:
setInterval(() => {
  fetch('/telemetry').then(r=>r.json()).then(d => {
    console.log(`Battery: ${d.battery}% | Status: ${d.status} | Charging: ${d.is_charging}`)
  })
}, 1000)
```

**Expected Behavior:**
```
1. Battery: 15% | Status: PATROLLING → RETURNING_HOME (auto-trigger)
2. Battery: 15% | Status: RETURNING_HOME (navigating to dock)
3. Battery: 15% | Status: DOCKED | Charging: true
4. Battery: 20% | Status: DOCKED | Charging: true (+5% every 10s)
5. Battery: 90% | Status: PATROLLING | Charging: false (auto-resume)
```

### **Test Geofencing & RTH**

**Create No-Fly Zone:**
1. Dashboard → Create Zone
2. Draw polygon around drone
3. Zone type: No-Fly
4. Save

**Expected:**
- Violation detected → RTH triggered
- Metrics incremented
- Telegram alert sent (if configured)

---

## 📦 **PRODUCTION DEPLOYMENT**

### **Deploy to Cloud (VPS/EC2/DigitalOcean)**

```bash
# SSH into server
ssh user@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone <repo-url>
cd hack

# Configure .env
nano .env

# Run with Docker
docker-compose up -d

# Enable auto-restart
docker-compose restart guardian-drone
```

### **Nginx Reverse Proxy (Optional)**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### **SSL/HTTPS (Let's Encrypt)**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🐛 **TROUBLESHOOTING**

### **Port Already in Use**
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or change port in app.py:
app.run(host='0.0.0.0', port=8081)
```

### **Camera Not Accessible**
- **Browser**: Must use `http://` (not HTTPS) for localhost
- **Permissions**: Allow camera access in browser settings
- **Docker**: Add `--device /dev/video0:/dev/video0` to docker-compose

### **Model Loading Slow**
- First run downloads YOLOv8 weights (~25MB)
- Subsequent runs use cached model
- Use GPU for faster inference (optional)

### **Cloudinary Upload Fails**
- Check `.env` credentials
- Verify API key is active
- Check quota (free tier: 25GB/month)

### **Telegram Not Working**
- Verify bot token is correct
- Check chat ID (use @userinfobot)
- Ensure bot added to chat/group

---

## 📚 **API DOCUMENTATION**

### **Core Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/telemetry` | GET | Drone telemetry data |
| `/detect_annotated` | POST | Run YOLO detection |
| `/metrics` | GET | Operational metrics |
| `/system_status` | GET | System health (RPi-dependent) |

### **Geofencing**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/zones/create` | POST | Create geofence zone |
| `/zones/list` | GET | List all zones |
| `/violations/recent` | GET | Recent violations |
| `/rth/trigger` | POST | Trigger return-to-home |

### **Phase-4 Docking**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dock/trigger` | POST | Manual dock trigger |
| `/dock/status` | GET | Docking/charging status |
| `/dock/set_location` | POST | Configure dock GPS |

### **Phase-4 Failures**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/failure/status` | GET | Failure handler status |
| `/failure/reset` | POST | Reset all failures |

---

## 🎓 **HACKATHON JUDGING NOTES**

### **Technical Excellence**

**Backend:**
- ✅ YOLOv8-VisDrone (aerial object detection)
- ✅ Flask RESTful API
- ✅ SQLite persistence (events, zones, violations, metrics)
- ✅ Cloudinary integration (image storage)
- ✅ Event engine with 5-second persistence rule
- ✅ Autonomous state machine (patrol → RTH → dock → charge → patrol)
- ✅ Failure recovery mechanisms

**Frontend:**
- ✅ Real-time telemetry (1s updates)
- ✅ Interactive Leaflet.js map
- ✅ Geofencing polygon drawing
- ✅ Operational metrics dashboard
- ✅ Security events log
- ✅ System health monitoring

### **Innovation**

- **Not just detection** → Full autonomous security platform
- **24/7 capable** → Self-docking, charging, recovery
- **Production-ready** → Docker, metrics, failure handling
- **Scalable** → Multi-RPi support via API

### **Real-World Applicability**

- **Campus Security**: Autonomous night patrols
- **Event Monitoring**: Crowd detection at festivals
- **Perimeter Defense**: No-fly zone enforcement
- **Industrial Safety**: Warehouse surveillance

---

## 📞 **SUPPORT**

**Issues?** Create GitHub issue with:
- System specs
- Error logs (`docker-compose logs`)
- Steps to reproduce

**Demo Request?** Contact for live walkthrough.

---

## 📄 **LICENSE**

MIT License - See LICENSE file

---

**Built for SIH/Dilaton PPI Hackathon**  
*"This isn't drone object detection. This is an Autonomous Campus Security Platform."*

🚁 **Ready to Deploy. Ready to Win.** 🏆
