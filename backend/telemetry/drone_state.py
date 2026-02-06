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
        
        # Raspberry Pi connection tracking
        self.rpi_connected = False
        self.rpi_last_update = 0
        self.rpi_timeout = 10  # seconds - if no update for 10s, consider disconnected
        self.rpi_latitude = None
        self.rpi_longitude = None
        self.rpi_speed = None
        self.rpi_camera_ok = False
        self.rpi_model_ok = False
        
        # Phase-4: Docking station support
        self.is_docked = False
        self.is_charging = False
        self.dock_latitude = self.base_lat  # Dock at home location
        self.dock_longitude = self.base_lon
        self.charging_rate = 5.0  # % per 10 seconds
        self.last_charge_time = 0
        
        # Simulation parameters
        self.patrol_radius = 0.0018  # degrees (~200m)
        self.battery_drain_rate = 0.5  # % per minute
        
        print(f"🚁 Drone initialized at ({self.latitude:.4f}, {self.longitude:.4f})")
    
    def update(self):
        """Update drone state (call every second)"""
        elapsed_time = time.time() - self.start_time
        
        # Check RPi connection status
        if time.time() - self.rpi_last_update > self.rpi_timeout:
            self.rpi_connected = False
            self.rpi_camera_ok = False
            self.rpi_model_ok = False
        
        # PHASE-4: Battery-driven autonomy
        if self.is_charging:
            # Charging cycle
            if time.time() - self.last_charge_time >= 10:
                self.battery = min(100, self.battery + self.charging_rate)
                self.last_charge_time = time.time()
                print(f"⚡ Charging: {self.battery:.1f}%")
                
                # Auto-resume patrol at 90%
                if self.battery >= 90:
                    self.is_charging = False
                    self.is_docked = False
                    self.status = "PATROLLING"
                    print("✅ Battery full - Resuming patrol")
        else:
            # Update battery (drains over time when not charging)
            minutes_elapsed = elapsed_time / 60.0
            self.battery = max(0, 100 - (self.battery_drain_rate * minutes_elapsed))
            
            # Auto-RTH on low battery (<20%)
            if self.battery < 20 and self.status != "RETURNING_HOME" and self.status != "DOCKING":
                self.status = "RETURNING_HOME"
                print(f"🚨 LOW BATTERY ({self.battery:.1f}%) - Auto RTH triggered")
        
        # Update status based on battery and docking
        if self.is_docked:
            if self.is_charging:
                self.status = "CHARGING"
            else:
                self.status = "DOCKED"
        elif self.status == "RETURNING_HOME":
            # Check if reached dock
            distance_to_dock = self._calculate_distance(
                self.latitude, self.longitude,
                self.dock_latitude, self.dock_longitude
            )
            if distance_to_dock < 0.00001:  # Very close (~1m)
                self.is_docked = True
                self.is_charging = True
                self.last_charge_time = time.time()
                self.status = "CHARGING"
                print("🔌 Docked - Charging started")
        elif self.battery > 20:
            if self.status not in ["PATROLLING", "READY"]:
                self.status = "PATROLLING"
        elif self.battery > 10:
            self.status = "LOW_BATTERY"
        
        # GPS position: Use RPi data if available, else simulate or use laptop location
        if self.rpi_connected and self.rpi_latitude is not None and self.rpi_longitude is not None:
            # Use Raspberry Pi GPS data
            self.latitude = self.rpi_latitude
            self.longitude = self.rpi_longitude
        elif self.status == "RETURNING_HOME" or self.status == "DOCKING":
            # Move toward dock
            self._move_toward_dock()
        else:
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
        
        # Speed: Use RPi data if available, else 0 if not connected, else simulate
        if self.rpi_connected and self.rpi_speed is not None:
            self.speed = self.rpi_speed
        elif not self.rpi_connected:
            self.speed = 0.0
        else:
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
            "timestamp": time.time(),
            "rpi_connected": self.rpi_connected,
            "is_docked": self.is_docked,
            "is_charging": self.is_charging,
            "dock_location": {
                "latitude": self.dock_latitude,
                "longitude": self.dock_longitude
            }
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
    
    def update_rpi_data(self, latitude=None, longitude=None, speed=None, camera_ok=False, model_ok=False):
        """Update data received from Raspberry Pi"""
        self.rpi_last_update = time.time()
        self.rpi_connected = True
        
        if latitude is not None:
            self.rpi_latitude = latitude
        if longitude is not None:
            self.rpi_longitude = longitude
        if speed is not None:
            self.rpi_speed = speed
        
        self.rpi_camera_ok = camera_ok
        self.rpi_model_ok = model_ok
    
    def get_system_health(self):
        """Get system health status for dashboard"""
        if self.rpi_connected:
            camera_status = "OK" if self.rpi_camera_ok else "ERROR"
            model_status = "RUNNING" if self.rpi_model_ok else "ERROR"
        else:
            camera_status = "DISCONNECTED"
            model_status = "DISCONNECTED"
        
        return {
            "camera": camera_status,
            "model": model_status,
            "server": "ONLINE",
            "rpi_connected": self.rpi_connected
        }
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate simple Euclidean distance between two GPS coordinates"""
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    
    def _move_toward_dock(self):
        """Move drone toward docking station"""
        # Calculate direction to dock
        delta_lat = self.dock_latitude - self.latitude
        delta_lon = self.dock_longitude - self.longitude
        distance = self._calculate_distance(self.latitude, self.longitude, self.dock_latitude, self.dock_longitude)
        
        if distance > 0.00001:  # Not at dock yet
            # Move step toward dock (simulate movement)
            step_size = 0.00005  # Small step per update
            self.latitude += (delta_lat / distance) * step_size
            self.longitude += (delta_lon / distance) * step_size
            
            # Update heading toward dock
            self.heading = int((math.degrees(math.atan2(delta_lon, delta_lat)) + 360) % 360)
        else:
            # At dock
            self.latitude = self.dock_latitude
            self.longitude = self.dock_longitude
    
    def trigger_dock(self):
        """Manually trigger docking sequence"""
        if not self.is_docked:
            self.status = "RETURNING_HOME"
            print("🔋 Manual dock trigger - Returning to dock")
    
    def set_dock_location(self, latitude, longitude):
        """Set docking station location"""
        self.dock_latitude = latitude
        self.dock_longitude = longitude
        print(f"🔌 Dock location set to ({latitude:.4f}, {longitude:.4f})")
