# 🚁 Campus Guardian Drone - Aerial Surveillance System

**Author:** Haryiank Kumra  
**License:** MIT  
**Version:** 1.0

An intelligent aerial surveillance system using YOLOv8 object detection trained on the VisDrone dataset for real-time monitoring from drone cameras. Designed for campus security, event monitoring, and autonomous aerial patrol operations.

---

## 📋 Table of Contents

1. [What is This?](#what-is-this)
2. [The AI Model](#the-ai-model)
3. [How It Works](#how-it-works)
4. [Website Features](#website-features)
5. [Drone Capabilities](#drone-capabilities)
6. [Quick Start](#quick-start)
7. [Deploy on Render](#deploy-on-render)
8. [Configuration](#configuration)
9. [API Endpoints](#api-endpoints)
10. [License](#license)

---

## 🎯 What is This?

Campus Guardian Drone is an **autonomous aerial surveillance system** that combines:
- **YOLOv8 object detection** trained on aerial/drone footage
- **Real-time video processing** from camera feeds
- **Autonomous flight operations** with geofencing
- **Cloud storage integration** (Cloudinary)
- **Live web dashboard** for monitoring

**Use Cases:**
- 🏫 Campus security monitoring
- 🚗 Parking lot management
- 📸 Event surveillance
- 🚨 Emergency response
- 🔍 Search and rescue operations

---

## 🤖 The AI Model

### YOLOv8-VisDrone

The system uses **YOLOv8s** (small variant) trained on the **VisDrone dataset**, specifically optimized for aerial/bird's-eye view object detection.

**Model Specifications:**
- **Architecture:** YOLOv8s (21MB)
- **Training Dataset:** VisDrone (aerial/drone imagery)
- **Input Size:** 640x480 pixels
- **Confidence Threshold:** 0.25
- **Framework:** Ultralytics YOLO

**Detection Capabilities:**
- 👤 Pedestrian & People
- 🚶 Bicycle & Motor
- 🚗 Car, Van, Truck, Bus
- 🛵 Tricycles & Awning-tricycles

### Why VisDrone Dataset?

Unlike standard YOLO trained on ground-level photos, VisDrone training enables:
- ✅ **Top-down view understanding** - Recognizes objects from aerial angles
- ✅ **Small object detection** - Detects distant vehicles and people
- ✅ **Crowded scene handling** - Works in high-density areas
- ✅ **Drone-specific optimizations** - Accounts for altitude, tilt, and movement

**Model Performance:**
- **FPS:** ~3-5 on CPU, ~15-20 on GPU
- **Accuracy:** High precision on aerial footage
- **Real-time:** Suitable for live monitoring

---

## ⚙️ How It Works

### System Architecture

```
┌─────────────────┐
│  Drone Camera   │ ──► Captures aerial video feed
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLOv8 Model   │ ──► Detects objects (cars, people, bikes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │ ──► Processes detections, stores events
└────────┬────────┘
         │
         ├──► Cloudinary (Image storage)
         ├──► SQLite (Event database)
         └──► CSV Logs (Audit trail)
         
         ▼
┌─────────────────┐
│  Web Dashboard  │ ──► Live visualization & controls
└─────────────────┘
```

### Detection Pipeline

1. **Video Input**
   - Webcam, RTSP stream, or video file
   - Frames captured at 640x480 resolution

2. **AI Processing**
   - YOLOv8 analyzes each frame
   - Detects target objects (vehicles, people, bikes)
   - Filters low-confidence detections (<0.25)

3. **Event Creation**
   - High-priority detections trigger events
   - Annotated images saved to Cloudinary
   - Event metadata stored in SQLite database
   - CSV log entry created with timestamp

4. **Live Dashboard**
   - Real-time telemetry updates (GPS, battery, altitude)
   - Detection feed with bounding boxes
   - Interactive map with drone position
   - System health monitoring

---

## 🌐 Website Features

### Dashboard (`http://localhost:8080`)

**Main Interface:**
- 🗺️ **Live Map** - Real-time drone position with Leaflet.js
- 📹 **Video Feed** - Annotated detections with bounding boxes
- 📊 **Telemetry Panel** - Battery, altitude, speed, GPS status
- 🔔 **Event Feed** - Recent detections with images
- ⚡ **System Health** - Camera, model, server status

**Analytics:**
- Total objects detected (people, vehicles)
- Detection timeline graph
- Patrol hours and uptime
- Battery usage statistics

**Controls:**
- 🏠 **Return-to-Home** - Emergency recall
- 🔌 **Docking** - Autonomous landing and charging
- 🚧 **Geofence Zones** - Set patrol/no-fly areas
- ⚙️ **Settings** - Confidence threshold, detection classes

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard home page |
| `/detect_annotated` | POST | Upload image, get detections |
| `/telemetry` | GET | Drone GPS, battery, altitude |
| `/system_status` | GET | Camera, model, server health |
| `/metrics` | GET | 24/7 operational statistics |
| `/rth/trigger` | POST | Return-to-home command |
| `/dock/trigger` | POST | Docking sequence |
| `/zones` | GET/POST | Geofencing management |
| `/security/events` | GET | Detection event history |

---

## 🚁 Drone Capabilities

### Autonomous Operations

**1. Patrol Mode**
- Autonomous flight within geofenced zones
- Continuous object detection
- Automatic event reporting
- Battery-aware operation

**2. Return-to-Home (RTH)**
- Triggered automatically at <20% battery
- Manual emergency recall available
- GPS-guided navigation to home point
- Altitude management during return

**3. Autonomous Docking & Charging**
- Precision landing on charging dock
- Automatic battery charging
- Resume patrol at 90% charge
- Failsafe for low battery emergencies

**4. Geofencing**
- Define patrol zones (allowed flight areas)
- No-fly zones (restricted areas)
- Automatic violation detection
- RTH trigger on boundary breach

### Telemetry System

Real-time monitoring of:
- 📍 **GPS Position** - Latitude, longitude, altitude
- 🔋 **Battery Level** - Percentage, voltage, charging status
- 🧭 **Heading** - Current direction (0-360°)
- 💨 **Speed** - Ground speed in m/s
- 🌡️ **Temperature** - System temperature
- 📡 **GPS Lock** - Satellite connection status

### Failure Recovery

**Built-in Safety Features:**
- Camera failure detection & retry
- Model crash recovery
- Connection loss handling
- Low battery auto-RTH
- Obstacle avoidance (with sensors)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Webcam or video source
- Cloudinary account (free tier works)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/HaryiankKumra/drone-aerial-view.git
cd drone-aerial-view

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Cloudinary credentials
```

### Configuration

Create `.env` file:

```bash
# Cloudinary (Required - Get from https://cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Model Settings
YOLO_MODEL=yolov8s-visdrone.pt
CONFIDENCE_THRESHOLD=0.25

# Optional: Telegram Alerts
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Run Locally

```bash
# Start the application
python app.py

# Open browser
# http://localhost:8080
```

---

## 🌐 Deploy on Render

### Step 1: Prepare Repository

Ensure you have:
- ✅ `requirements.txt` (dependencies)
- ✅ `render.yaml` (Render configuration)
- ✅ `.env.example` (template for secrets)
- ✅ All code committed to GitHub

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### Step 3: Deploy Web Service

#### Option A: Auto-Deploy (Recommended)

1. **New Web Service**
   - Dashboard → "New +" → "Web Service"
   - Select your GitHub repo: `drone-aerial-view`

2. **Configure Service**
   ```
   Name: campus-guardian-drone
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

3. **Add Environment Variables**
   - Go to "Environment" tab
   - Add secrets:
     ```
     CLOUDINARY_CLOUD_NAME=your_value
     CLOUDINARY_API_KEY=your_value
     CLOUDINARY_API_SECRET=your_value
     YOLO_MODEL=yolov8s-visdrone.pt
     CONFIDENCE_THRESHOLD=0.25
     FLASK_ENV=production
     PORT=8080
     ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build (~5-10 minutes)
   - Your app will be live at: `https://campus-guardian-drone.onrender.com`

#### Option B: Blueprint Deploy

If you have `render.yaml`:

```bash
# render.yaml should contain:
services:
  - type: web
    name: campus-guardian-drone
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: YOLO_MODEL
        value: yolov8s-visdrone.pt
      - key: FLASK_ENV
        value: production
```

### Step 4: Configure Model Storage

**Important:** Render's free tier has limited storage. Options:

**Option 1: Use HuggingFace API (Recommended for Free Tier)**
```bash
# In .env on Render
HUGGINGFACE_API_KEY=hf_your_token_here
# App will automatically use cloud inference
```

**Option 2: Include Model in Repo**
```bash
# Add to .gitattributes
*.pt filter=lfs diff=lfs merge=lfs -text

# Use Git LFS for large model file
git lfs install
git lfs track "*.pt"
git add .gitattributes yolov8s-visdrone.pt
git commit -m "Add model with Git LFS"
```

### Step 5: Post-Deployment

1. **Verify Deployment**
   - Visit your Render URL
   - Check `/system_status` endpoint
   - Test detection with sample image

2. **Monitor Logs**
   - Render Dashboard → "Logs" tab
   - Watch for startup messages
   - Verify model loading

3. **Set Up Alerts** (Optional)
   - Add `TELEGRAM_BOT_TOKEN` to environment
   - Configure Telegram notifications

### Deployment Notes

**Free Tier Limitations:**
- ⚠️ Service spins down after 15min inactivity
- ⚠️ 512MB RAM (use HuggingFace API for model)
- ⚠️ Limited disk space (model in repo or use HF)

**Upgrade for Production:**
- ✅ Starter Plan: $7/month (always-on, 512MB RAM)
- ✅ Standard Plan: $25/month (2GB RAM, faster)
- ✅ Persistent disk for model caching

---

## 📐 Configuration

### Model Settings (`config.py`)

```python
MODEL_PATH = 'yolov8s-visdrone.pt'  # Model file
CONF_THRESHOLD = 0.25                # Detection confidence (0.0-1.0)
TARGET_CLASSES = [                   # Objects to detect
    'pedestrian', 'people', 'bicycle', 'car', 
    'van', 'truck', 'bus', 'motor'
]
```

### Video Source

```python
VIDEO_SOURCE = 'auto'           # Auto-detect webcam
# VIDEO_SOURCE = 0               # Webcam index
# VIDEO_SOURCE = 'rtsp://...'   # RTSP stream
# VIDEO_SOURCE = 'video.mp4'    # Video file
```

### Frame Settings

```python
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SHOW_FPS = True
SHOW_CONF = True
```

---

## 🔌 API Endpoints

### Core Endpoints

#### GET `/`
Dashboard home page

#### POST `/detect_annotated`
**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "total_objects": 3,
  "detections": [
    {
      "class": "car",
      "confidence": 0.89,
      "bbox": [100, 150, 300, 400]
    }
  ],
  "annotated_image": "data:image/jpeg;base64,..."
}
```

#### GET `/telemetry`
**Response:**
```json
{
  "latitude": 30.3560,
  "longitude": 76.3649,
  "altitude": 15.5,
  "battery": 85.3,
  "speed": 2.5,
  "heading": 45,
  "status": "PATROL",
  "gps_lock": true
}
```

#### GET `/system_status`
**Response:**
```json
{
  "server_status": "ONLINE",
  "camera_status": "CONNECTED",
  "model_status": "LOADED",
  "gps_status": "LOCK",
  "uptime_hours": 12.5
}
```

---

## 📊 Project Structure

```
campus-guardian-drone/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── storage.py                # Event storage logic
├── cloudinary_storage.py     # Image upload to cloud
├── csv_logger.py             # CSV audit logs
├── hf_inference.py           # HuggingFace API client
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment config
├── .env.example             # Environment template
├── LICENSE                  # MIT License
├── README.md               # This file
├── backend/
│   ├── telemetry/          # Drone telemetry system
│   ├── geofencing.py       # Zone management
│   ├── event_engine.py     # Event processing
│   ├── metrics.py          # Analytics
│   └── failure_handler.py  # Error recovery
├── static/                 # CSS, JavaScript
├── templates/              # HTML templates
├── data/                   # SQLite databases
├── recordings/             # Logs and recordings
└── yolov8s-visdrone.pt    # AI model (21MB)
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

**Copyright © 2026 Haryiank Kumra**

---

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8 framework
- **VisDrone** - Aerial detection dataset
- **Cloudinary** - Image storage platform
- **Render** - Deployment platform

---

## 📧 Contact

**Haryiank Kumra**  
GitHub: [@HaryiankKumra](https://github.com/HaryiankKumra)

---

## 🎯 Future Roadmap

- [ ] Real drone integration (DJI SDK)
- [ ] Multi-drone coordination
- [ ] Advanced analytics dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Face recognition (with privacy compliance)
- [ ] Crowd density heatmaps
- [ ] Automated incident reports
- [ ] Integration with security systems

---
