# FREE Deployment Guide - Aerial Drone Surveillance

## 🚀 Deploy to Render.com (100% FREE - No Credit Card)

### Step 1: Prepare Your Code

1. Make sure all files are in the `hack` folder:
   - ✅ `app.py` (Flask API)
   - ✅ `templates/index.html` (Dashboard)
   - ✅ `requirements-deploy.txt` (Dependencies)
   - ✅ `yolov8s-visdrone.pt` (Model weights)
   - ✅ `render.yaml` (Render config)

### Step 2: Create GitHub Repository

```bash
cd "/Users/mohitkumra/Desktop/DL Notebooks/hack"

# Initialize git (if not already)
git init

# Add all files
git add app.py templates/ requirements-deploy.txt yolov8s-visdrone.pt render.yaml

# Commit
git commit -m "Aerial surveillance app ready for deployment"

# Create repo on GitHub and push
# Go to github.com, create new repository (e.g., "drone-surveillance")
# Then:
git remote add origin https://github.com/YOUR_USERNAME/drone-surveillance.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render

1. **Sign up on Render.com** (FREE, no credit card):
   - Go to https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub account

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `drone-surveillance` repo

3. **Configure Service**:
   - **Name**: `drone-surveillance`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-deploy.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300`
   - **Plan**: Select **FREE** tier

4. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://drone-surveillance.onrender.com`

### Step 4: Access Your Dashboard

Once deployed, visit:
```
https://your-app-name.onrender.com
```

You'll see the dashboard with:
- ✅ Live camera feed
- ✅ Real-time object detection
- ✅ Detection statistics
- ✅ Object counts

---

## 🎯 Alternative: Deploy to PythonAnywhere (Also FREE)

### PythonAnywhere Setup

1. **Sign up** at https://www.pythonanywhere.com (FREE account)

2. **Upload Files**:
   - Go to "Files" tab
   - Create folder: `/home/YOUR_USERNAME/drone-surveillance`
   - Upload all files

3. **Install Dependencies**:
   ```bash
   # Open Bash console
   cd drone-surveillance
   pip install --user -r requirements-deploy.txt
   ```

4. **Configure Web App**:
   - Go to "Web" tab → "Add new web app"
   - Choose "Manual configuration" → Python 3.10
   - Set source code: `/home/YOUR_USERNAME/drone-surveillance`
   - Set WSGI file to point to `app.py`

5. **Reload** and visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## 🔌 API Endpoints

### 1. Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "model": "yolov8s-visdrone",
  "classes": ["pedestrian", "people", "bicycle", "car", ...]
}
```

### 2. Detect (JSON Response)
```bash
POST /detect
Content-Type: application/json

Body:
{
  "image": "data:image/jpeg;base64,/9j/4AAQ..."
}

Response:
{
  "success": true,
  "detections": [
    {
      "class": "car",
      "confidence": 0.87,
      "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
    }
  ],
  "total_objects": 5,
  "counts": {"car": 3, "pedestrian": 2}
}
```

### 3. Detect with Annotated Image
```bash
POST /detect_annotated
Content-Type: application/json

Body:
{
  "image": "data:image/jpeg;base64,/9j/4AAQ..."
}

Response:
{
  "success": true,
  "annotated_image": "data:image/jpeg;base64,...",
  "detections": [...],
  "total_objects": 5,
  "counts": {...}
}
```

---

## 📱 Use from Mobile/Drone

### Option 1: Direct Dashboard Access
Simply open your deployed URL on any device with a camera:
```
https://your-app-name.onrender.com
```

### Option 2: API Integration (Python)
```python
import requests
import base64

# Read image
with open('drone_image.jpg', 'rb') as f:
    img_data = base64.b64encode(f.read()).decode()

# Send to API
response = requests.post(
    'https://your-app-name.onrender.com/detect',
    json={'image': f'data:image/jpeg;base64,{img_data}'}
)

detections = response.json()
print(f"Found {detections['total_objects']} objects!")
```

### Option 3: API Integration (JavaScript/Mobile)
```javascript
// Capture from camera
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
ctx.drawImage(video, 0, 0);

// Send to API
const imageData = canvas.toDataURL('image/jpeg');
const response = await fetch('https://your-app-name.onrender.com/detect', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: imageData})
});

const data = await response.json();
console.log('Detections:', data.detections);
```

---

## ⚡ Free Tier Limits

### Render.com Free Tier:
- ✅ 750 hours/month runtime
- ✅ Auto-sleep after 15 min inactivity
- ✅ Wakes up on request (~30s delay)
- ✅ 512 MB RAM
- ✅ Shared CPU

### PythonAnywhere Free Tier:
- ✅ Always-on web app
- ✅ 512 MB storage
- ✅ 100k hits/day
- ✅ 1 web worker

---

## 🎥 Testing Locally First

Before deploying, test locally:

```bash
# Run Flask app
python app.py

# Open browser
http://localhost:5000

# Or test API with curl
curl http://localhost:5000/health
```

---

## 🛠️ Troubleshooting

**Issue**: Model not loading
- Make sure `yolov8s-visdrone.pt` is committed to GitHub
- Check file size < 100MB (GitHub limit)
- If too large, use Git LFS or download on startup

**Issue**: Camera not working
- Enable HTTPS (Render provides it automatically)
- Browsers require HTTPS for camera access

**Issue**: Slow detection
- Render free tier has limited CPU
- Reduce image size before sending
- Increase detection interval (500ms → 1000ms)

---

## 🎉 You're Done!

Your aerial surveillance system is now:
- ✅ **Deployed for FREE**
- ✅ **Accessible from anywhere**
- ✅ **No credit card required**
- ✅ **Works on mobile/desktop**
- ✅ **API ready for drone integration**

Share your deployed URL with anyone to use the dashboard! 🚁
