# 🎥 Camera Access Fix

## Problem: "Camera Access Denied" on Localhost

### ✅ Quick Fix (2 steps):

#### **Step 1: Check Browser Permissions**

**Chrome/Brave:**
1. Look for **camera icon** with ❌ in address bar (left side)
2. Click it → Change to **"Allow"**
3. Refresh page (F5)

**Safari:**
1. Settings → Websites → Camera
2. Find "localhost" → Change to **"Allow"**
3. Refresh page

**Firefox:**
1. Click 🔒 lock icon in address bar
2. Permissions → Camera → Allow
3. Refresh page

---

#### **Step 2: Use Correct URL**

✅ **WORKS:**
- http://localhost:8080
- http://127.0.0.1:8080

❌ **BLOCKED:**
- http://192.168.x.x:8080 (your local IP - requires HTTPS)

---

### 🔧 If Still Not Working:

**Option 1: Test Camera Access**
```javascript
// Open browser console (F12) and paste:
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => console.log("✅ Camera works!", stream))
  .catch(err => console.error("❌ Error:", err));
```

**Option 2: Clear Site Data**
1. Chrome: Settings → Privacy → Clear browsing data
2. Check "Site settings" only
3. Clear → Refresh localhost:8080

**Option 3: Use Different Browser**
- Try Firefox or Brave if Chrome blocks

---

### 📱 Alternative for Hackathon Demo:

If camera still blocked, use **pre-recorded video**:
1. Record drone footage on phone
2. Upload to app (we can add upload feature)
3. Process video instead of live feed

---

## Current Setup:
- ✅ App running on: http://localhost:8080
- ✅ Server healthy
- ⏳ Waiting for camera permission

**Open:** http://localhost:8080  
**Click:** "Start Detection"  
**Allow camera when prompted**
