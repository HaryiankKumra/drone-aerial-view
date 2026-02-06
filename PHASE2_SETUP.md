# 🚨 PHASE-2 SETUP GUIDE
## Event Engine + Security Intelligence

**Phase-2 transforms your drone from "detection demo" to "enterprise security system"**

---

## ✅ WHAT'S NEW IN PHASE-2

### 🧠 Event Engine
- **5-second persistence rule**: Events created only if object detected for 5+ seconds
- **Severity classification**: HIGH (people), MEDIUM (vehicles), LOW (litter)
- **SQLite database**: All events persist across sessions
- **Event log panel**: Filter by severity, view snapshots, click for details

### 🔔 Telegram Alerts
- Real-time notifications to your phone
- Includes event details + snapshot image
- Configurable alert levels (HIGH/MEDIUM only by default)

### 📊 Event Statistics
- Total events counter
- Breakdown by severity level
- Event history with timestamps

---

## 🚀 QUICK START

### 1. Install Dependencies

```bash
# Already installed if you completed Phase-1
pip install requests  # For Telegram API
```

### 2. Setup Telegram Bot (Optional but Recommended)

#### Step 1: Create Bot
1. Open Telegram app
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts to create your bot
5. **Save the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Step 2: Get Chat ID
1. Send a message to your new bot (any message)
2. Visit this URL in browser (replace `<YOUR_BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` in the response
4. **Save that chat ID**

#### Step 3: Configure Environment
Add to your `.env` file:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### Step 4: Test Connection
```bash
curl http://localhost:8080/security/telegram/test
```

Should return:
```json
{
  "success": true,
  "message": "Connected to @your_bot_name",
  "enabled": true
}
```

---

## 📊 HOW IT WORKS

### Event Creation Flow

```
1. Camera captures frame
2. YOLO detects person
3. Detection buffer updated (timestamp)
4. After 5 seconds of continuous detection...
5. ✅ EVENT CREATED!
6. Event saved to SQLite database
7. If severity = HIGH/MEDIUM → Telegram alert sent
8. Event appears in dashboard
9. Detection buffer cleared for that object type
```

### Severity Rules

| Object Type | Severity | Alert? |
|------------|----------|--------|
| person, people | HIGH | ✅ Yes |
| bicycle, car, van, truck, bus, motor | MEDIUM | ✅ Yes |
| litter, trash, debris | LOW | ❌ No |

You can modify these in `backend/event_engine/engine.py`

---

## 🎯 API ENDPOINTS (NEW)

### Get Recent Events
```bash
GET /security/events?limit=50&severity=HIGH
```

Response:
```json
{
  "success": true,
  "events": [
    {
      "event_id": "EVT-A1B2C3D4",
      "timestamp": "2026-02-06T23:15:30",
      "object_type": "person",
      "severity": "HIGH",
      "confidence": 0.87,
      "drone_lat": 30.3560,
      "drone_lon": 76.3649,
      "zone": "Campus Area",
      "snapshot_url": "https://cloudinary.com/...",
      "bbox_data": "{...}"
    }
  ],
  "total": 15
}
```

### Get Event Details
```bash
GET /security/event/EVT-A1B2C3D4
```

### Get Event Statistics
```bash
GET /security/stats
```

Response:
```json
{
  "success": true,
  "stats": {
    "total_events": 42,
    "high_severity": 15,
    "medium_severity": 20,
    "low_severity": 7
  }
}
```

---

## 📱 DASHBOARD FEATURES

### Event Log Panel
- **Filter buttons**: ALL, HIGH, MEDIUM, LOW
- **Event cards**: Color-coded by severity
- **Click event**: View full details
- **Auto-refresh**: Updates every 5 seconds
- **Statistics bar**: Total and severity breakdown

### Event Card Information
- 🚨/⚠️/ℹ️ Severity emoji
- Object type (PERSON, CAR, etc.)
- Event ID (EVT-XXXXXXXX)
- Timestamp
- Zone location
- Confidence percentage
- Snapshot image (if available)

---

## 🎓 DEMO SCRIPT FOR JUDGES

> **"In Phase-2, we introduced an event engine that converts raw detections into security incidents with severity classification, alerts, and evidence logging."**

**Show them:**

1. **Event Persistence**
   - Point camera at person for 5 seconds
   - Event appears in dashboard
   - Refresh page → event still there ✅

2. **Severity Classification**
   - Show HIGH severity event (person) in red
   - Show MEDIUM severity event (vehicle) in orange
   - Explain color coding

3. **Telegram Alert**
   - Trigger HIGH severity event
   - Show alert on phone in real-time
   - Show snapshot included

4. **Filter & Search**
   - Click filter buttons (HIGH, MEDIUM, LOW)
   - Show event counts update
   - Click event card for details

5. **Statistics**
   - Point to stats bar
   - Explain cumulative tracking
   - Show database persistence

**Judge-proof line:**
> "This isn't just detection—it's an intelligent security system with event correlation, severity analysis, and multi-channel alerting."

---

## 🔧 CUSTOMIZATION

### Change Persistence Threshold
Edit `backend/event_engine/engine.py`:
```python
self.persistence_threshold = 5  # Change to 3 or 10 seconds
```

### Add New Severity Levels
Edit `backend/event_engine/engine.py`:
```python
SEVERITY_MAP = {
    'person': 'HIGH',
    'car': 'MEDIUM',
    'bicycle': 'LOW',  # Move bicycle to LOW
    'dog': 'CRITICAL'  # Add new level
}
```

### Change Alert Conditions
Edit `backend/event_engine/engine.py`:
```python
def should_alert(self, event_id):
    event = self.db.get_event_by_id(event_id)
    # Alert only on CRITICAL
    return event['severity'] == 'CRITICAL'
```

### Add Email Alerts
Create `backend/event_engine/email_bot.py` similar to `telegram_bot.py`, then import and call in app.py

---

## 🐛 TROUBLESHOOTING

### Telegram Not Working
```bash
# Check configuration
curl http://localhost:8080/security/telegram/test

# Common issues:
# 1. Wrong bot token → Check @BotFather
# 2. Wrong chat ID → Visit /getUpdates URL
# 3. Bot not started → Send /start to your bot first
# 4. Missing .env → Copy .env.example to .env
```

### Events Not Appearing
```bash
# Check database
sqlite3 data/events.db "SELECT COUNT(*) FROM events;"

# Check API
curl http://localhost:8080/security/events

# Check detection buffer
# Point camera at person for 5+ seconds
# Watch terminal for "🎯 Event created: EVT-XXXXXXXX"
```

### No High Severity Events
- Make sure detecting "people" or "person" class
- Check YOLO confidence (must be > 0.25)
- Wait full 5 seconds for persistence rule
- Check `SEVERITY_MAP` in `engine.py`

---

## 📈 PHASE-2 PASS CRITERIA

✅ 5-second persistence rule working
✅ Events saved to database
✅ Event log panel visible in UI
✅ Severity classification working
✅ At least ONE alert channel (Telegram)
✅ Statistics updating
✅ Events persist after page refresh

**If all ✅ → Phase-2 COMPLETE** 🎉

---

## ⏭️ WHAT'S NEXT?

**Phase-3: Geofencing & Autonomous Patrol**
- Define no-fly zones on map
- Restricted area detection
- Polygon-based geofencing
- Autonomous return-to-home
- Battery-based abort logic

---

## 💡 PRO TIPS

1. **For demo**: Set persistence to 3 seconds for faster response
2. **For production**: Keep at 5-10 seconds to avoid false positives
3. **Multiple alerts**: Add email, SMS, webhook—impress judges
4. **Custom zones**: Change "Campus Area" to specific building names
5. **Evidence**: Snapshots are your killer feature—emphasize them

---

## 🎯 SUCCESS METRICS

After Phase-2, you should have:
- ✅ **Zero per-frame spam**: Events only on sustained detection
- ✅ **Intelligent classification**: Severity-based prioritization
- ✅ **Real-time alerts**: Telegram notifications
- ✅ **Persistent logs**: SQLite database
- ✅ **Professional UI**: Event cards with filters
- ✅ **Judge-ready demo**: Clear, impressive, enterprise-level

**You're now building something nobody can ignore.** 💥
