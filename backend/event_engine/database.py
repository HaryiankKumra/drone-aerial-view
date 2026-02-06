"""
Event Database Schema for Campus Guardian
SQLite-based event persistence
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class EventDatabase:
    def __init__(self, db_path='data/events.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                object_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence REAL NOT NULL,
                drone_lat REAL,
                drone_lon REAL,
                zone TEXT DEFAULT 'Campus Area',
                snapshot_url TEXT,
                snapshot_path TEXT,
                bbox_data TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL
            )
        ''')
        
        # Detection accumulator (for 5-second rule)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_buffer (
                object_type TEXT,
                first_seen TEXT,
                last_seen TEXT,
                count INTEGER,
                avg_confidence REAL,
                PRIMARY KEY (object_type)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                event_id TEXT,
                alert_type TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                recipient TEXT,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_event(self, event_data):
        """Create a new security event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (
                event_id, timestamp, object_type, severity, confidence,
                drone_lat, drone_lon, zone, snapshot_url, snapshot_path,
                bbox_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['event_id'],
            event_data['timestamp'],
            event_data['object_type'],
            event_data['severity'],
            event_data['confidence'],
            event_data.get('drone_lat'),
            event_data.get('drone_lon'),
            event_data.get('zone', 'Campus Area'),
            event_data.get('snapshot_url'),
            event_data.get('snapshot_path'),
            json.dumps(event_data.get('bbox_data', {})),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return event_data['event_id']
    
    def get_events(self, limit=50, severity=None):
        """Get recent events"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if severity:
            cursor.execute('''
                SELECT * FROM events 
                WHERE severity = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (severity, limit))
        else:
            cursor.execute('''
                SELECT * FROM events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_event_by_id(self, event_id):
        """Get specific event details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM events WHERE event_id = ?', (event_id,))
        event = cursor.fetchone()
        conn.close()
        
        return dict(event) if event else None
    
    def update_detection_buffer(self, object_type, confidence):
        """Update detection buffer for 5-second persistence rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT * FROM detection_buffer WHERE object_type = ?
        ''', (object_type,))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE detection_buffer 
                SET last_seen = ?, count = count + 1, avg_confidence = ?
                WHERE object_type = ?
            ''', (now, confidence, object_type))
        else:
            cursor.execute('''
                INSERT INTO detection_buffer (object_type, first_seen, last_seen, count, avg_confidence)
                VALUES (?, ?, ?, 1, ?)
            ''', (object_type, now, now, confidence))
        
        conn.commit()
        conn.close()
    
    def check_persistence(self, object_type, threshold_seconds=5):
        """Check if object has been detected for threshold seconds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT first_seen, count, avg_confidence FROM detection_buffer 
            WHERE object_type = ?
        ''', (object_type,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, 0
        
        first_seen = datetime.fromisoformat(result[0])
        duration = (datetime.now() - first_seen).total_seconds()
        
        return duration >= threshold_seconds, result[2]  # Returns (passed, confidence)
    
    def clear_detection_buffer(self, object_type=None):
        """Clear detection buffer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if object_type:
            cursor.execute('DELETE FROM detection_buffer WHERE object_type = ?', (object_type,))
        else:
            cursor.execute('DELETE FROM detection_buffer')
        
        conn.commit()
        conn.close()
    
    def log_alert(self, event_id, alert_type, recipient):
        """Log alert sent"""
        import uuid
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        alert_id = f"ALT-{uuid.uuid4().hex[:8]}"
        
        cursor.execute('''
            INSERT INTO alerts (alert_id, event_id, alert_type, sent_at, recipient)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_id, event_id, alert_type, datetime.now().isoformat(), recipient))
        
        conn.commit()
        conn.close()
        
        return alert_id
    
    def get_stats(self):
        """Get event statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low
            FROM events
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'total_events': stats[0],
            'high_severity': stats[1] or 0,
            'medium_severity': stats[2] or 0,
            'low_severity': stats[3] or 0
        }
