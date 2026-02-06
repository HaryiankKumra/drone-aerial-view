"""
Campus Guardian Drone - System Simulator
Simulates all system functionality without hardware for testing
"""

import requests
import time
import json
import base64
import random
from datetime import datetime
from PIL import Image
import io

BASE_URL = "http://localhost:8080"

class DroneSimulator:
    def __init__(self):
        self.base_url = BASE_URL
        print("🚁 Campus Guardian Drone - System Simulator")
        print("=" * 60)
        
    def create_fake_image(self):
        """Create a fake base64 image for testing"""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    
    def print_response(self, title, response):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"📡 {title}")
        print(f"{'='*60}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
        print()
    
    def test_telemetry(self):
        """Test: Get drone telemetry"""
        print("\n🔍 TEST 1: Get Telemetry")
        response = requests.get(f"{self.base_url}/telemetry")
        self.print_response("Telemetry Data", response)
        return response.json() if response.status_code == 200 else None
    
    def test_system_status(self):
        """Test: Get system health"""
        print("\n🔍 TEST 2: System Health Status")
        response = requests.get(f"{self.base_url}/system_status")
        self.print_response("System Health", response)
    
    def test_metrics(self):
        """Test: Get operational metrics"""
        print("\n🔍 TEST 3: Operational Metrics")
        response = requests.get(f"{self.base_url}/metrics")
        self.print_response("24/7 Metrics", response)
    
    def test_rpi_connection(self):
        """Test: Simulate Raspberry Pi sending data"""
        print("\n🔍 TEST 4: Simulate RPi Connection")
        
        payload = {
            "device_id": "RPi-SIM-01",
            "location": "Simulated Campus Gate",
            "timestamp": datetime.now().isoformat(),
            "image": self.create_fake_image(),
            "gps_latitude": 30.3560 + random.uniform(-0.0005, 0.0005),
            "gps_longitude": 76.3649 + random.uniform(-0.0005, 0.0005),
            "speed": random.uniform(2.0, 5.0),
            "camera_ok": True,
            "model_ok": True
        }
        
        response = requests.post(
            f"{self.base_url}/rpi/detect",
            json=payload
        )
        self.print_response("RPi Detection Result", response)
        
        # Check if RPi is now connected
        print("\n✅ Checking RPi connection status...")
        time.sleep(1)
        status = requests.get(f"{self.base_url}/system_status")
        data = status.json()
        print(f"RPi Connected: {data.get('rpi_connected', False)}")
    
    def test_create_zones(self):
        """Test: Create geofence zones"""
        print("\n🔍 TEST 5: Create Geofence Zones")
        
        # Create patrol zone
        patrol_zone = {
            "name": "Test Patrol Zone",
            "zone_type": "patrol",
            "coordinates": [
                [30.3555, 76.3645],
                [30.3558, 76.3645],
                [30.3558, 76.3648],
                [30.3555, 76.3648]
            ],
            "min_altitude": 0,
            "max_altitude": 50
        }
        
        response = requests.post(
            f"{self.base_url}/zones/create",
            json=patrol_zone
        )
        self.print_response("Patrol Zone Created", response)
        
        # Create no-fly zone
        nofly_zone = {
            "name": "Test No-Fly Zone",
            "zone_type": "no_fly",
            "coordinates": [
                [30.3565, 76.3645],
                [30.3568, 76.3645],
                [30.3568, 76.3648],
                [30.3565, 76.3648]
            ],
            "min_altitude": 0,
            "max_altitude": 100
        }
        
        response = requests.post(
            f"{self.base_url}/zones/create",
            json=nofly_zone
        )
        self.print_response("No-Fly Zone Created", response)
        
        # List all zones
        response = requests.get(f"{self.base_url}/zones/list")
        self.print_response("All Zones", response)
    
    def test_trigger_violation(self):
        """Test: Trigger zone violation"""
        print("\n🔍 TEST 6: Trigger Zone Violation")
        
        # Move drone into no-fly zone
        violation_location = {
            "latitude": 30.3566,
            "longitude": 76.3646
        }
        
        response = requests.post(
            f"{self.base_url}/update_location",
            json=violation_location
        )
        self.print_response("Location Update (Should Trigger Violation)", response)
        
        # Check violations
        time.sleep(1)
        response = requests.get(f"{self.base_url}/violations/recent?hours=1")
        self.print_response("Recent Violations", response)
        
        # Get violation stats
        response = requests.get(f"{self.base_url}/violations/stats")
        self.print_response("Violation Statistics", response)
    
    def test_rth_trigger(self):
        """Test: Trigger Return-to-Home"""
        print("\n🔍 TEST 7: Trigger Return-to-Home")
        
        payload = {
            "reason": "manual_override",
            "emergency": False
        }
        
        response = requests.post(
            f"{self.base_url}/rth/trigger",
            json=payload
        )
        self.print_response("RTH Triggered", response)
        
        # Check RTH status
        time.sleep(1)
        response = requests.get(f"{self.base_url}/rth/status")
        self.print_response("RTH Status", response)
        
        # Check telemetry for RTH state
        response = requests.get(f"{self.base_url}/telemetry")
        data = response.json()
        print(f"\n✅ Drone Status: {data.get('status', 'UNKNOWN')}")
        print(f"✅ RTH Active: {data.get('rth_active', False)}")
    
    def test_docking(self):
        """Test: Trigger docking sequence"""
        print("\n🔍 TEST 8: Trigger Docking Sequence")
        
        response = requests.post(f"{self.base_url}/dock/trigger")
        self.print_response("Docking Triggered", response)
        
        # Check docking status
        time.sleep(1)
        response = requests.get(f"{self.base_url}/dock/status")
        self.print_response("Docking Status", response)
        
        # Set custom dock location
        dock_location = {
            "latitude": 30.3558,
            "longitude": 76.3647
        }
        response = requests.post(
            f"{self.base_url}/dock/set_location",
            json=dock_location
        )
        self.print_response("Dock Location Set", response)
    
    def test_failure_handler(self):
        """Test: Check failure handler status"""
        print("\n🔍 TEST 9: Failure Handler Status")
        
        response = requests.get(f"{self.base_url}/failure/status")
        self.print_response("Failure Handler Status", response)
    
    def test_security_events(self):
        """Test: Get security events"""
        print("\n🔍 TEST 10: Security Events")
        
        # Get all events
        response = requests.get(f"{self.base_url}/security/events?limit=10")
        self.print_response("Recent Security Events", response)
        
        # Get event statistics
        response = requests.get(f"{self.base_url}/security/stats")
        self.print_response("Event Statistics", response)
    
    def simulate_autonomous_cycle(self):
        """Test: Simulate autonomous charging cycle"""
        print("\n🔍 TEST 11: Autonomous Cycle Simulation")
        print("\n⚡ Monitoring autonomous loop...")
        print("Watch the dashboard for real-time updates!")
        print("\nPress Ctrl+C to stop monitoring\n")
        
        try:
            for i in range(10):
                response = requests.get(f"{self.base_url}/telemetry")
                data = response.json()
                
                status = data.get('status', 'UNKNOWN')
                battery = data.get('battery', 0)
                is_charging = data.get('is_charging', False)
                is_docked = data.get('is_docked', False)
                
                print(f"[{i+1}/10] Battery: {battery:.1f}% | Status: {status} | "
                      f"Charging: {is_charging} | Docked: {is_docked}")
                
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("🚀 STARTING COMPLETE SYSTEM SIMULATION")
        print("="*60)
        print("\n⏰ Waiting 2 seconds for server to be ready...")
        time.sleep(2)
        
        try:
            # Test 1: Basic telemetry
            self.test_telemetry()
            
            # Test 2: System health
            self.test_system_status()
            
            # Test 3: Metrics
            self.test_metrics()
            
            # Test 4: RPi simulation
            self.test_rpi_connection()
            
            # Test 5: Create zones
            self.test_create_zones()
            
            # Test 6: Trigger violation
            self.test_trigger_violation()
            
            # Test 7: RTH
            self.test_rth_trigger()
            
            # Test 8: Docking
            self.test_docking()
            
            # Test 9: Failure handler
            self.test_failure_handler()
            
            # Test 10: Security events
            self.test_security_events()
            
            # Test 11: Autonomous cycle
            self.simulate_autonomous_cycle()
            
            print("\n" + "="*60)
            print("✅ ALL TESTS COMPLETED!")
            print("="*60)
            print("\n📊 Check your dashboard at: http://localhost:8080")
            print("You should see:")
            print("  → RPi status changed from DISCONNECTED to CONNECTED")
            print("  → Geofence zones created on map")
            print("  → Violations logged")
            print("  → Metrics updated")
            print("  → System status reflecting changes")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Cannot connect to server!")
            print("Make sure the server is running on http://localhost:8080")
            print("\nStart server with:")
            print("  source .venv/bin/activate")
            print("  python app.py")
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


def continuous_monitoring():
    """Continuously monitor and display system state"""
    print("\n🔄 CONTINUOUS MONITORING MODE")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            response = requests.get(f"{BASE_URL}/telemetry")
            data = response.json()
            
            print(f"\r⏱️  {datetime.now().strftime('%H:%M:%S')} | "
                  f"Battery: {data.get('battery', 0):.1f}% | "
                  f"Status: {data.get('status', 'UNKNOWN'):15s} | "
                  f"GPS: {data.get('latitude', 0):.5f}, {data.get('longitude', 0):.5f} | "
                  f"Speed: {data.get('speed', 0):.1f}m/s", 
                  end='', flush=True)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
    except:
        print("\n❌ Server not available")


if __name__ == "__main__":
    import sys
    
    simulator = DroneSimulator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        continuous_monitoring()
    else:
        simulator.run_all_tests()
        
        print("\n" + "="*60)
        print("💡 TIP: Run continuous monitoring with:")
        print("   python simulate_system.py monitor")
        print("="*60 + "\n")
