"""
Return-to-Home (RTH) Autonomous Flight System
Handles autonomous navigation back to home position
"""

import math
from typing import Tuple, List, Dict
from datetime import datetime

class ReturnToHome:
    """Manages autonomous return-to-home functionality"""
    
    # RTH trigger reasons
    REASON_NO_FLY_VIOLATION = "no_fly_violation"
    REASON_LOW_BATTERY = "low_battery"
    REASON_MANUAL = "manual"
    REASON_ALTITUDE_VIOLATION = "altitude_violation"
    REASON_EMERGENCY = "emergency"
    
    def __init__(self, home_lat: float = 30.3560, home_lon: float = 76.3649):
        """
        Initialize RTH system
        
        Args:
            home_lat: Home position latitude (default: TIET Library)
            home_lon: Home position longitude
        """
        self.home_position = (home_lat, home_lon)
        self.rth_active = False
        self.rth_triggered_at = None
        self.rth_reason = None
        self.rth_waypoints = []
        self.current_waypoint_index = 0
        
        print(f"✅ RTH initialized - Home: ({home_lat}, {home_lon})")
    
    def set_home_position(self, lat: float, lon: float):
        """Update home position"""
        self.home_position = (lat, lon)
        print(f"📍 Home position updated: ({lat}, {lon})")
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula
        
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate bearing from point 1 to point 2
        
        Returns:
            Bearing in degrees (0-360)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360
        bearing_deg = (bearing_deg + 360) % 360
        
        return bearing_deg
    
    def generate_waypoints(
        self, 
        current_lat: float, 
        current_lon: float, 
        waypoint_distance: float = 50.0
    ) -> List[Tuple[float, float]]:
        """
        Generate intermediate waypoints from current position to home
        
        Args:
            current_lat: Current drone latitude
            current_lon: Current drone longitude
            waypoint_distance: Distance between waypoints in meters
        
        Returns:
            List of (lat, lon) waypoints
        """
        home_lat, home_lon = self.home_position
        
        # Calculate total distance
        total_distance = self.calculate_distance(current_lat, current_lon, home_lat, home_lon)
        
        # If very close to home, go direct
        if total_distance <= waypoint_distance:
            return [(home_lat, home_lon)]
        
        # Calculate bearing to home
        bearing = self.calculate_bearing(current_lat, current_lon, home_lat, home_lon)
        
        # Generate waypoints
        waypoints = []
        num_waypoints = int(total_distance / waypoint_distance)
        
        for i in range(1, num_waypoints + 1):
            fraction = i / num_waypoints
            # Simple linear interpolation (good enough for short distances)
            wp_lat = current_lat + (home_lat - current_lat) * fraction
            wp_lon = current_lon + (home_lon - current_lon) * fraction
            waypoints.append((wp_lat, wp_lon))
        
        # Always end at home
        if waypoints[-1] != (home_lat, home_lon):
            waypoints.append((home_lat, home_lon))
        
        return waypoints
    
    def trigger_rth(
        self, 
        current_lat: float, 
        current_lon: float, 
        reason: str,
        emergency: bool = False
    ) -> Dict:
        """
        Trigger return-to-home sequence
        
        Args:
            current_lat: Current drone latitude
            current_lon: Current drone longitude
            reason: Reason for RTH trigger
            emergency: If True, generate direct path (no waypoints)
        
        Returns:
            RTH info dictionary
        """
        self.rth_active = True
        self.rth_triggered_at = datetime.now().isoformat()
        self.rth_reason = reason
        self.current_waypoint_index = 0
        
        # Generate waypoints
        if emergency:
            # Direct path to home
            self.rth_waypoints = [self.home_position]
        else:
            # Waypoints every 50 meters
            self.rth_waypoints = self.generate_waypoints(current_lat, current_lon, 50.0)
        
        home_lat, home_lon = self.home_position
        distance_to_home = self.calculate_distance(current_lat, current_lon, home_lat, home_lon)
        bearing_to_home = self.calculate_bearing(current_lat, current_lon, home_lat, home_lon)
        
        # Estimate time (assuming 5 m/s average speed)
        estimated_time = distance_to_home / 5.0
        
        print(f"🚨 RTH TRIGGERED: {reason}")
        print(f"   Distance to home: {distance_to_home:.1f}m")
        print(f"   Bearing: {bearing_to_home:.1f}°")
        print(f"   Waypoints: {len(self.rth_waypoints)}")
        print(f"   Estimated time: {estimated_time:.1f}s")
        
        return {
            'active': True,
            'triggered_at': self.rth_triggered_at,
            'reason': reason,
            'emergency': emergency,
            'waypoints': self.rth_waypoints,
            'total_waypoints': len(self.rth_waypoints),
            'current_waypoint': 0,
            'distance_to_home': distance_to_home,
            'bearing_to_home': bearing_to_home,
            'estimated_time': estimated_time
        }
    
    def get_next_waypoint(self) -> Tuple[float, float]:
        """
        Get the next waypoint to navigate to
        
        Returns:
            (lat, lon) tuple or None if reached home
        """
        if not self.rth_active:
            return None
        
        if self.current_waypoint_index >= len(self.rth_waypoints):
            # Reached home
            return None
        
        waypoint = self.rth_waypoints[self.current_waypoint_index]
        return waypoint
    
    def advance_waypoint(self):
        """Move to next waypoint"""
        if self.rth_active:
            self.current_waypoint_index += 1
            
            if self.current_waypoint_index >= len(self.rth_waypoints):
                # RTH complete
                self.complete_rth()
    
    def complete_rth(self):
        """Mark RTH as complete"""
        if self.rth_active:
            print(f"✅ RTH COMPLETE - Reason: {self.rth_reason}")
            self.rth_active = False
            self.rth_triggered_at = None
            self.rth_reason = None
            self.rth_waypoints = []
            self.current_waypoint_index = 0
    
    def cancel_rth(self):
        """Cancel RTH (manual override)"""
        if self.rth_active:
            print(f"⚠️  RTH CANCELLED - Was triggered for: {self.rth_reason}")
            self.rth_active = False
            self.rth_triggered_at = None
            self.rth_reason = None
            self.rth_waypoints = []
            self.current_waypoint_index = 0
    
    def get_status(self, current_lat: float = None, current_lon: float = None) -> Dict:
        """
        Get current RTH status
        
        Args:
            current_lat: Optional current position for distance calculation
            current_lon: Optional current position for distance calculation
        
        Returns:
            Status dictionary
        """
        if not self.rth_active:
            return {
                'active': False,
                'home_position': self.home_position
            }
        
        status = {
            'active': True,
            'triggered_at': self.rth_triggered_at,
            'reason': self.rth_reason,
            'home_position': self.home_position,
            'total_waypoints': len(self.rth_waypoints),
            'current_waypoint': self.current_waypoint_index,
            'progress_percent': (self.current_waypoint_index / len(self.rth_waypoints) * 100) if self.rth_waypoints else 0
        }
        
        # Add current distance/bearing if position provided
        if current_lat is not None and current_lon is not None:
            home_lat, home_lon = self.home_position
            status['distance_to_home'] = self.calculate_distance(current_lat, current_lon, home_lat, home_lon)
            status['bearing_to_home'] = self.calculate_bearing(current_lat, current_lon, home_lat, home_lon)
        
        return status
