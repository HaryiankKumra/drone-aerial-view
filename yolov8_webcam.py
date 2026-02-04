"""
Aerial Drone Surveillance - Real-time Object Detection
Uses YOLOv8 trained on VisDrone dataset for TOP-DOWN view detection
"""

import cv2
import time
import os
# import requests  # Uncomment when API integration is ready
from ultralytics import YOLO
from config import (
    MODEL_PATH, CONF_THRESHOLD, TARGET_CLASSES, VIDEO_SOURCE,
    FRAME_WIDTH, FRAME_HEIGHT, SHOW_FPS, SHOW_CONF,
    BOX_COLOR, TEXT_COLOR, USE_API, API_ENDPOINT
)


def find_available_camera():
    """Find the first available camera (indexes 0-3)"""
    for cam_index in range(4):
        temp_cap = cv2.VideoCapture(cam_index)
        if temp_cap.isOpened():
            print(f"✓ Using camera index: {cam_index}")
            return temp_cap
        temp_cap.release()
    return None


def init_video_source(source):
    """Initialize video source (camera, RTSP, or video file)"""
    if source == 'auto':
        cap = find_available_camera()
        if cap is None:
            print("✗ Error: Could not open any webcam (tried indexes 0-3).")
            exit()
    elif isinstance(source, int):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"✗ Error: Could not open camera {source}")
            exit()
    elif isinstance(source, str):
        # RTSP stream or video file
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"✗ Error: Could not open source: {source}")
            exit()
        print(f"✓ Opened video source: {source}")
    else:
        cap = cv2.VideoCapture(source)
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return cap


def send_to_api(frame, detections):
    """
    Send frame and detections to API endpoint (for future deployment)
    Uncomment when API is ready
    """
    # payload = {
    #     'detections': detections,
    #     'timestamp': time.time()
    # }
    # _, buffer = cv2.imencode('.jpg', frame)
    # files = {'image': buffer.tobytes()}
    # try:
    #     response = requests.post(API_ENDPOINT, data=payload, files=files, timeout=1)
    #     return response.json()
    # except Exception as e:
    #     print(f"API error: {e}")
    #     return None
    pass


def main():
    """Main detection loop"""
    
    # Load YOLOv8 model
    print(f"Loading model: {MODEL_PATH}")
    print("⚡ Optimized for Mac M4 with Neural Engine acceleration")
    
    model = YOLO(MODEL_PATH)
    print("✓ Model loaded successfully")
    print("⚠️  NOTE: Using standard COCO model - limited accuracy for top-down views")
    print("   For production aerial detection, train on VisDrone dataset")
    
    # Initialize video source
    cap = init_video_source(VIDEO_SOURCE)
    
    prev_time = 0
    frame_count = 0
    
    print("\n" + "="*60)
    print("AERIAL SURVEILLANCE - REAL-TIME OBJECT DETECTION")
    print("="*60)
    print(f"Model: {MODEL_PATH}")
    print(f"Confidence threshold: {CONF_THRESHOLD}")
    print(f"Target classes: {', '.join(TARGET_CLASSES)}")
    print(f"Press 'q' to quit")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("✗ Error: Failed to grab frame")
            break
        
        frame_count += 1
        
        # Run inference
        results = model(frame, verbose=False)[0]
        
        # Process detections
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.model.names[cls_id]
            conf = float(box.conf[0])
            
            # Filter by class and confidence
            if class_name not in TARGET_CLASSES or conf < CONF_THRESHOLD:
                continue
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Store detection info for API
            detections.append({
                'class': class_name,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })
            
            # Draw bounding box
            label = f"{class_name} {conf:.2f}" if SHOW_CONF else class_name
            cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
            
            # Draw label background
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), BOX_COLOR, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        
        # Display FPS
        if SHOW_FPS:
            fps_text = f"FPS: {fps:.1f}"
            cv2.rectangle(frame, (5, 5), (120, 40), (0, 0, 0), -1)
            cv2.putText(frame, fps_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)
        
        # Display detection count
        count_text = f"Objects: {len(detections)}"
        cv2.putText(frame, count_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)
        
        # Send to API (future feature)
        if USE_API and len(detections) > 0:
            send_to_api(frame, detections)
        
        # Show frame
        cv2.imshow("Aerial Surveillance - YOLOv8 VisDrone", frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n✓ Shutting down...")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print(f"✓ Processed {frame_count} frames")
    print("✓ Done")


if __name__ == "__main__":
    main()
