"""
HuggingFace Inference API Client for YOLO Detection
Offloads ML inference to HuggingFace's serverless infrastructure
"""
import os
import requests
import base64
from io import BytesIO
from PIL import Image
import numpy as np

class HuggingFaceYOLO:
    """Client for HuggingFace Inference API"""
    
    def __init__(self, model_id="mshamrai/yolov8s-visdrone"):
        """Initialize HF client
        
        Args:
            model_id: HuggingFace model repository (default: mshamrai/yolov8s-visdrone)
        """
        self.api_token = os.getenv('HUGGINGFACE_API_KEY')
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        
    def predict(self, image, conf=0.25):
        """Run YOLO detection on image via HuggingFace API
        
        Args:
            image: PIL Image or numpy array
            conf: Confidence threshold (0.0-1.0)
            
        Returns:
            List of detections with format compatible with ultralytics YOLO
        """
        # Convert image to bytes
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
            
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        
        # Call HuggingFace API
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=image_bytes,
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            # Transform HF format to ultralytics format
            detections = self._transform_results(results, conf)
            return detections
            
        except requests.exceptions.RequestException as e:
            print(f"❌ HuggingFace API error: {e}")
            return []
    
    def _transform_results(self, hf_results, conf_threshold):
        """Transform HuggingFace detection format to ultralytics format
        
        HF format: [{"label": "car", "score": 0.95, "box": {"xmin": 10, "ymin": 20, "xmax": 100, "ymax": 200}}]
        
        Returns: List of dicts compatible with our existing code
        """
        detections = []
        
        for det in hf_results:
            if det.get('score', 0) < conf_threshold:
                continue
                
            box = det.get('box', {})
            detections.append({
                'class': det.get('label', 'unknown'),
                'confidence': det.get('score', 0),
                'bbox': {
                    'x1': box.get('xmin', 0),
                    'y1': box.get('ymin', 0),
                    'x2': box.get('xmax', 0),
                    'y2': box.get('ymax', 0)
                }
            })
        
        return detections
    
    def __call__(self, image, conf=0.25):
        """Make instance callable like YOLO model"""
        return self.predict(image, conf)


# Environment check helper
def use_huggingface_api():
    """Check if we should use HuggingFace API instead of local model"""
    # Use HF API if:
    # 1. API key is set AND
    # 2. We're on Vercel (VERCEL env var) OR model file doesn't exist
    has_api_key = bool(os.getenv('HUGGINGFACE_API_KEY'))
    is_vercel = bool(os.getenv('VERCEL'))
    no_local_model = not os.path.exists('yolov8n-visdrone.pt')
    
    return has_api_key and (is_vercel or no_local_model)
