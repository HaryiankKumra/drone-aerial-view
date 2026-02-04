"""
Flask API for Aerial Drone Surveillance - FREE Deployment Ready
Receives images from camera, runs YOLOv8 detection, returns results
"""
from flask import Flask, request, jsonify, render_template, Response
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json

app = Flask(__name__)

# Load model once at startup
print("Loading YOLOv8-VisDrone model...")
model = YOLO('yolov8s-visdrone.pt')
print("Model loaded successfully!")

# Configuration
CONF_THRESHOLD = 0.25
TARGET_CLASSES = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor']

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'yolov8s-visdrone',
        'classes': TARGET_CLASSES
    })

@app.route('/detect', methods=['POST'])
def detect():
    """
    Main detection endpoint
    Accepts: JSON with base64 encoded image or multipart/form-data with image file
    Returns: JSON with detections
    """
    try:
        # Handle base64 image from JSON
        if request.is_json:
            data = request.get_json()
            image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
            image = Image.open(BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Process detections
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            # Filter by target classes
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2)
                    }
                })
        
        # Count objects by class
        counts = {}
        for det in detections:
            counts[det['class']] = counts.get(det['class'], 0) + 1
        
        return jsonify({
            'success': True,
            'detections': detections,
            'total_objects': len(detections),
            'counts': counts,
            'image_size': {
                'width': frame.shape[1],
                'height': frame.shape[0]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/detect_annotated', methods=['POST'])
def detect_annotated():
    """
    Detection endpoint that returns annotated image
    Returns: JSON with base64 encoded annotated image and detections
    """
    try:
        # Handle base64 image
        if request.is_json:
            data = request.get_json()
            image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
            image = Image.open(BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Draw annotations
        annotated_frame = frame.copy()
        detections = []
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                # Draw bounding box
                color = (0, 255, 0)  # Green
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f'{class_name}: {conf:.2f}'
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                })
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Count objects
        counts = {}
        for det in detections:
            counts[det['class']] = counts.get(det['class'], 0) + 1
        
        return jsonify({
            'success': True,
            'annotated_image': f'data:image/jpeg;base64,{img_base64}',
            'detections': detections,
            'total_objects': len(detections),
            'counts': counts
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=8080, debug=False)
