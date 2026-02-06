"""
Violation Detection and Logging System
Tracks zone violations and triggers alerts
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class ViolationDetector:
    """Detects zone violations in real-time"""
    
    def __init__(self, zone_manager):
        """Initialize with ZoneManager instance"""
        self.zone_manager = zone_manager
        self.current_violations = {}  # Track active violations to avoid spam
    
    def check_position(self, lat: float, lon: float, altitude: float) -> Dict:
        """
        Check if current position violates any zones
        
        Returns:
            {
                'violation': bool,
                'zone': dict or None,
                'violation_type': str ('no_fly', 'altitude', 'restricted'),
                'severity': str ('CRITICAL', 'HIGH', 'MEDIUM'),
                'action_required': str ('RTH', 'ALERT', 'LOG')
            }
        """
        # Check no-fly zones (CRITICAL)
        is_no_fly, no_fly_zone = self.zone_manager.is_in_no_fly_zone(lat, lon)
        if is_no_fly:
            return {
                'violation': True,
                'zone': no_fly_zone,
                'violation_type': 'no_fly',
                'severity': 'CRITICAL',
                'action_required': 'RTH',
                'message': f"CRITICAL: Drone entered no-fly zone '{no_fly_zone['name']}'"
            }
        
        # Check altitude violations in restricted zones
        containing_zones = self.zone_manager.get_zones_containing_point(lat, lon)
        for zone in containing_zones:
            if zone['zone_type'] == 'restricted' and altitude > zone['max_altitude']:
                return {
                    'violation': True,
                    'zone': zone,
                    'violation_type': 'altitude',
                    'severity': 'HIGH',
                    'action_required': 'ALERT',
                    'message': f"HIGH: Altitude {altitude}m exceeds limit {zone['max_altitude']}m in '{zone['name']}'"
                }
        
        # No violations
        return {
            'violation': False,
            'zone': None,
            'violation_type': None,
            'severity': None,
            'action_required': None,
            'message': 'Position OK'
        }
    
    def should_trigger_rth(self, violation_result: Dict) -> bool:
        """Determine if Return-to-Home should be triggered"""
        if not violation_result['violation']:
            return False
        
        # RTH on CRITICAL violations (no-fly zones)
        return violation_result['severity'] == 'CRITICAL'


class ViolationLogger:
    """Logs all zone violations to database"""
    
    def __init__(self, db_path: str = "data/violations.db"):
        """Initialize violation logger"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create violations table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                zone_id INTEGER,
                zone_name TEXT,
                zone_type TEXT,
                violation_type TEXT CHECK(violation_type IN ('no_fly', 'altitude', 'restricted')),
                severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
                drone_lat REAL NOT NULL,
                drone_lon REAL NOT NULL,
                drone_altitude REAL,
                action_taken TEXT,
                snapshot_url TEXT,
                resolution_time TEXT,
                notes TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_violations_timestamp 
            ON violations(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_violations_severity 
            ON violations(severity)
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Violation database initialized: {self.db_path}")
    
    def log_violation(
        self, 
        zone: Dict, 
        violation_type: str, 
        severity: str,
        drone_lat: float,
        drone_lon: float,
        drone_altitude: float,
        action_taken: str = "",
        snapshot_url: str = ""
    ) -> int:
        """
        Log a zone violation
        
        Returns:
            violation_id
        """
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO violations
            (timestamp, zone_id, zone_name, zone_type, violation_type, severity,
             drone_lat, drone_lon, drone_altitude, action_taken, snapshot_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            zone.get('zone_id') if zone else None,
            zone.get('name') if zone else 'Unknown',
            zone.get('zone_type') if zone else 'unknown',
            violation_type,
            severity,
            drone_lat,
            drone_lon,
            drone_altitude,
            action_taken,
            snapshot_url
        ))
        
        violation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"⚠️  Violation logged: {violation_type} - {severity} - ID: {violation_id}")
        return violation_id
    
    def get_recent_violations(self, limit: int = 50) -> List[Dict]:
        """Get recent violations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM violations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_violations_by_severity(self, severity: str) -> List[Dict]:
        """Get violations filtered by severity"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM violations WHERE severity = ? ORDER BY timestamp DESC",
            (severity,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get violation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total violations
        cursor.execute("SELECT COUNT(*) FROM violations")
        total = cursor.fetchone()[0]
        
        # By severity
        cursor.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")
        severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By violation type
        cursor.execute("SELECT violation_type, COUNT(*) FROM violations GROUP BY violation_type")
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Today's violations
        cursor.execute(
            "SELECT COUNT(*) FROM violations WHERE date(timestamp) = date('now')"
        )
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_violations': total,
            'today': today_count,
            'by_severity': severity_counts,
            'by_type': type_counts
        }
    
    def mark_resolved(self, violation_id: int, notes: str = "") -> bool:
        """Mark a violation as resolved"""
        resolution_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE violations SET resolution_time = ?, notes = ? WHERE violation_id = ?",
            (resolution_time, notes, violation_id)
        )
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
