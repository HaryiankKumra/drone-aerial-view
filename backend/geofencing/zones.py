"""
Zone Management System
Handles creation, storage, and querying of geofencing zones
"""

import sqlite3
import json
from datetime import datetime
from shapely.geometry import Point, Polygon
from typing import List, Dict, Optional, Tuple

class ZoneManager:
    """Manages geofencing zones with polygon storage"""
    
    # Zone types
    ZONE_PATROL = "patrol"
    ZONE_RESTRICTED = "restricted"
    ZONE_NO_FLY = "no_fly"
    
    def __init__(self, db_path: str = "data/zones.db"):
        """Initialize zone manager with database connection"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create zones table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zones (
                zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                zone_type TEXT NOT NULL CHECK(zone_type IN ('patrol', 'restricted', 'no_fly')),
                polygon_coords TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT DEFAULT 'admin',
                is_active INTEGER DEFAULT 1,
                description TEXT,
                max_altitude REAL DEFAULT 100.0,
                alert_on_entry INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Zone database initialized: {self.db_path}")
    
    def create_zone(
        self, 
        name: str, 
        zone_type: str, 
        polygon_coords: List[Tuple[float, float]], 
        description: str = "",
        max_altitude: float = 100.0,
        alert_on_entry: bool = True
    ) -> int:
        """
        Create a new geofencing zone
        
        Args:
            name: Human-readable zone name (e.g., "Library No-Fly Zone")
            zone_type: patrol, restricted, or no_fly
            polygon_coords: List of (lat, lon) tuples defining the polygon
            description: Optional zone description
            max_altitude: Maximum allowed altitude in zone (meters)
            alert_on_entry: Whether to send alert on zone entry
        
        Returns:
            zone_id of the created zone
        """
        if zone_type not in [self.ZONE_PATROL, self.ZONE_RESTRICTED, self.ZONE_NO_FLY]:
            raise ValueError(f"Invalid zone type: {zone_type}")
        
        if len(polygon_coords) < 3:
            raise ValueError("Polygon must have at least 3 points")
        
        # Store coordinates as JSON
        coords_json = json.dumps(polygon_coords)
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO zones 
            (name, zone_type, polygon_coords, created_at, description, max_altitude, alert_on_entry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, zone_type, coords_json, timestamp, description, max_altitude, int(alert_on_entry)))
        
        zone_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Zone created: {name} ({zone_type}) - ID: {zone_id}")
        return zone_id
    
    def get_all_zones(self, active_only: bool = True) -> List[Dict]:
        """Get all zones from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM zones"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        zones = []
        for row in rows:
            zone = dict(row)
            # Parse JSON coordinates
            zone['polygon_coords'] = json.loads(zone['polygon_coords'])
            zone['alert_on_entry'] = bool(zone['alert_on_entry'])
            zone['is_active'] = bool(zone['is_active'])
            zones.append(zone)
        
        return zones
    
    def get_zone_by_id(self, zone_id: int) -> Optional[Dict]:
        """Get a specific zone by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM zones WHERE zone_id = ?", (zone_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        zone = dict(row)
        zone['polygon_coords'] = json.loads(zone['polygon_coords'])
        zone['alert_on_entry'] = bool(zone['alert_on_entry'])
        zone['is_active'] = bool(zone['is_active'])
        
        return zone
    
    def delete_zone(self, zone_id: int) -> bool:
        """Soft delete a zone (set is_active = 0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE zones SET is_active = 0 WHERE zone_id = ?", (zone_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            print(f"✅ Zone {zone_id} deleted")
            return True
        return False
    
    def permanently_delete_zone(self, zone_id: int) -> bool:
        """Permanently delete a zone from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM zones WHERE zone_id = ?", (zone_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            print(f"✅ Zone {zone_id} permanently deleted")
            return True
        return False
    
    def point_in_zone(self, lat: float, lon: float, zone_id: int) -> bool:
        """Check if a point is inside a specific zone"""
        zone = self.get_zone_by_id(zone_id)
        if not zone:
            return False
        
        point = Point(lon, lat)  # Shapely uses (x, y) = (lon, lat)
        # Convert [(lat, lon), ...] to [(lon, lat), ...]
        polygon_coords_xy = [(coord[1], coord[0]) for coord in zone['polygon_coords']]
        polygon = Polygon(polygon_coords_xy)
        
        return polygon.contains(point)
    
    def get_zones_containing_point(self, lat: float, lon: float) -> List[Dict]:
        """Get all zones that contain a given point"""
        zones = self.get_all_zones()
        point = Point(lon, lat)
        
        containing_zones = []
        for zone in zones:
            # Convert [(lat, lon), ...] to [(lon, lat), ...]
            polygon_coords_xy = [(coord[1], coord[0]) for coord in zone['polygon_coords']]
            polygon = Polygon(polygon_coords_xy)
            
            if polygon.contains(point):
                containing_zones.append(zone)
        
        return containing_zones
    
    def get_no_fly_zones(self) -> List[Dict]:
        """Get all active no-fly zones"""
        all_zones = self.get_all_zones()
        return [z for z in all_zones if z['zone_type'] == self.ZONE_NO_FLY]
    
    def is_in_no_fly_zone(self, lat: float, lon: float) -> Tuple[bool, Optional[Dict]]:
        """
        Check if point is in any no-fly zone
        
        Returns:
            (is_violation, zone_info) tuple
        """
        no_fly_zones = self.get_no_fly_zones()
        point = Point(lon, lat)
        
        for zone in no_fly_zones:
            polygon_coords_xy = [(coord[1], coord[0]) for coord in zone['polygon_coords']]
            polygon = Polygon(polygon_coords_xy)
            
            if polygon.contains(point):
                return True, zone
        
        return False, None
    
    def get_statistics(self) -> Dict:
        """Get zone statistics"""
        zones = self.get_all_zones(active_only=False)
        
        stats = {
            'total_zones': len(zones),
            'active_zones': len([z for z in zones if z['is_active']]),
            'patrol_zones': len([z for z in zones if z['zone_type'] == self.ZONE_PATROL]),
            'restricted_zones': len([z for z in zones if z['zone_type'] == self.ZONE_RESTRICTED]),
            'no_fly_zones': len([z for z in zones if z['zone_type'] == self.ZONE_NO_FLY])
        }
        
        return stats
