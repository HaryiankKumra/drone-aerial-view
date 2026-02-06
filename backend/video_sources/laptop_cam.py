"""
Laptop/Webcam Video Source
Simulates drone feed from laptop camera for development/testing
"""
import cv2
from .base import VideoSource

class LaptopCam(VideoSource):
    """Webcam video source (for development and testing)"""
    
    def __init__(self, camera_index=0):
        """
        Initialize laptop camera
        Args:
            camera_index: Camera device index (0 = default)
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        
        # Set optimal resolution for drone simulation
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print(f"✅ LaptopCam initialized (simulating drone feed)")
    
    def get_frame(self):
        """Read frame from webcam"""
        if not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def release(self):
        """Release webcam resources"""
        if self.cap:
            self.cap.release()
            print("🔌 LaptopCam released")
    
    def is_available(self):
        """Check if webcam is accessible"""
        return self.cap and self.cap.isOpened()
    
    def get_resolution(self):
        """Get current camera resolution"""
        if not self.is_available():
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.release()
