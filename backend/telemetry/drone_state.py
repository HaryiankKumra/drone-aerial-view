"""
Drone State and Telemetry Simulator
Generates realistic drone telemetry data for Campus Guardian system
"""
import time
import random
import math

class DroneState:
    """Simulates real-time drone telemetry data"""
    
    def __init__(self, start_location=(30.3560, 76.3649)):
        """
        Initialize drone state
        Args:
            start_location: (latitude, longitude) starting position
        """
        self.start_time = time.time()
        self.base_lat, self.base_lon = start_location
        
        # Initial state
        self.latitude = self.base_lat
        self.longitude = self.base_lon
        self.altitude = 2.0  # meters (fixed at 2m)
        self.temperature = 25.0  # celsius (will be updated from browser)
        self.battery = 100.0  # percentage
        self.status = "READY"
        self.mode = "AUTO"
        self.gps_lock = True
        self.speed = 0.0  # m/s
        self.heading = 0  # degrees (0-360)
        self.patrol_pattern = "diamond"  # diamond or circle
        
        # Simulation parameters
        self.patrol_radius = 0.0018  # degrees (~200m)
        self.battery_drain_rate = 0.5  # % per minute
        
        print(f"🚁 Drone initialized at ({self.latitude:.4f}, {self.longitude:.4f})")
    
    def update(self):
        """Update drone state (call every second)"""
        elapsed_time = time.time() - self.start_time
        
        # Update status based on battery
        if self.battery > 20:
            self.status = "PATROLLING"
        elif self.battery > 10:
            self.status = "LOW_BATTERY"
        else:
            self.status = "RETURNING_HOME"
        
        # Simulate GPS movement (diamond or circular patrol pattern)
        if self.patrol_pattern == "diamond":
            # Diamond pattern: 4 corners
            progress = (elapsed_time * 0.05) % 4  # Complete diamond every ~80s
            corner = int(progress)
            t = progress - corner
            
            # Diamond corners (N, E, S, W)
            corners = [
                (self.patrol_radius, 0),      # North
                (0, self.patrol_radius),      # East
                (-self.patrol_radius, 0),     # South
                (0, -self.patrol_radius)      # West
            ]
            
            # Interpolate between corners
            start = corners[corner]
            end = corners[(corner + 1) % 4]
            
            lat_offset = start[0] + (end[0] - start[0]) * t
            lon_offset = start[1] + (end[1] - start[1]) * t
            
            self.latitude = self.base_lat + lat_offset
            self.longitude = self.base_lon + lon_offset
            
            # Calculate heading based on movement direction
            angle_to_next = math.atan2(end[1] - start[1], end[0] - start[0])
            self.heading = int((math.degrees(angle_to_next) + 90) % 360)
        else:
            # Circular patrol pattern
            angle = (elapsed_time * 0.1) % (2 * math.pi)
            self.latitude = self.base_lat + (self.patrol_radius * math.cos(angle))
            self.longitude = self.base_lon + (self.patrol_radius * math.sin(angle))
            self.heading = int((math.degrees(angle) + 90) % 360)
        
        # Fixed altitude at 2 meters
        self.altitude = 2.0
        
        # Update battery (drains over time)
        minutes_elapsed = elapsed_time / 60.0
        self.battery = max(0, 100 - (self.battery_drain_rate * minutes_elapsed))
        
        # Simulate speed (varying between 0-5 m/s)
        self.speed = abs(3.0 + (2.0 * math.sin(elapsed_time * 0.3)))
        
        # GPS lock is always true for now (can simulate loss later)
        self.gps_lock = True
    
    def get_telemetry(self):
        """Get current telemetry data as dictionary"""
        self.update()
        
        return {
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude, 1),
            "temperature": round(self.temperature, 1),
            "battery": round(self.battery, 1),
            "status": self.status,
            "mode": self.mode,
            "gps_lock": self.gps_lock,
            "speed": round(self.speed, 1),
            "heading": self.heading,
            "patrol_pattern": self.patrol_pattern,
            "timestamp": time.time()
        }
    
    def get_hud_data(self):
        """Get formatted HUD display data"""
        self.update()
        
        return {
            "alt": f"{self.altitude:.0f}m",
            "bat": f"{self.battery:.0f}%",
            "mode": self.mode,
            "gps": "LOCK" if self.gps_lock else "NO LOCK",
            "spd": f"{self.speed:.1f}m/s",
            "hdg": f"{self.heading}°"
        }
    
    def update_location(self, latitude, longitude):
        """Update base location from browser geolocation"""
        self.base_lat = latitude
        self.base_lon = longitude
        self.latitude = latitude
        self.longitude = longitude
        print(f"📍 Drone location updated to ({latitude:.4f}, {longitude:.4f})")
    
    def update_temperature(self, temp):
        """Update temperature from browser/weather API"""
        self.temperature = temp
    
    def set_patrol_pattern(self, pattern):
        """Set patrol pattern: 'diamond' or 'circle'"""
        if pattern in ["diamond", "circle"]:
            self.patrol_pattern = pattern
            print(f"🔄 Patrol pattern changed to: {pattern}")
    
    def reset(self):
        """Reset drone to initial state"""
        self.__init__((self.base_lat, self.base_lon))
