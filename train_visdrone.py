"""
Train YOLOv8 on VisDrone Dataset for Aerial Detection
This script will guide you through training your own aerial detection model
"""

import os
import sys
from pathlib import Path

def create_visdrone_yaml():
    """Create VisDrone dataset configuration file"""
    
    yaml_content = """# VisDrone Dataset Configuration for YOLOv8
# Dataset: http://aiskyeye.com/

# Paths (relative to this file)
path: ./visdrone_data
train: images/train
val: images/val

# Classes (VisDrone Detection Classes)
names:
  0: pedestrian
  1: people
  2: bicycle
  3: car
  4: van
  5: truck
  6: tricycle
  7: awning-tricycle
  8: bus
  9: motor
"""
    
    with open('VisDrone.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("✓ Created VisDrone.yaml configuration file")


def main():
    print("="*70)
    print("YOLOv8 VisDrone Training Setup")
    print("="*70)
    print()
    
    print("This script will help you train YOLOv8 on VisDrone dataset")
    print("for accurate TOP-DOWN aerial object detection.")
    print()
    
    # Check if dataset exists
    if not os.path.exists('visdrone_data'):
        print("STEP 1: Download VisDrone Dataset")
        print("-" * 70)
        print()
        print("1. Visit: https://github.com/VisDrone/VisDrone-Dataset")
        print("   or: http://aiskyeye.com/")
        print()
        print("2. Download these files:")
        print("   - VisDrone2019-DET-train.zip")
        print("   - VisDrone2019-DET-val.zip")
        print()
        print("3. Create folder structure:")
        print("   mkdir -p visdrone_data/images/train")
        print("   mkdir -p visdrone_data/images/val")
        print("   mkdir -p visdrone_data/labels/train")
        print("   mkdir -p visdrone_data/labels/val")
        print()
        print("4. Extract the downloaded files into visdrone_data/")
        print()
        
        cont = input("Have you downloaded and extracted the dataset? (y/n): ").lower()
        if cont != 'y':
            print("\n✗ Please download the dataset first, then run this script again.")
            sys.exit(0)
    else:
        print("✓ Found visdrone_data directory")
    
    print()
    print("STEP 2: Create Dataset Configuration")
    print("-" * 70)
    
    if os.path.exists('VisDrone.yaml'):
        print("✓ VisDrone.yaml already exists")
    else:
        create_visdrone_yaml()
    
    print()
    print("STEP 3: Start Training")
    print("-" * 70)
    print()
    print("Training command:")
    print()
    print("  yolo detect train data=VisDrone.yaml model=yolov8n.pt epochs=50 imgsz=640 batch=16")
    print()
    print("Training parameters:")
    print("  - model: yolov8n.pt (nano - fastest)")
    print("  - epochs: 50 (increase to 100+ for better accuracy)")
    print("  - imgsz: 640 (image size)")
    print("  - batch: 16 (reduce to 8 if you run out of memory)")
    print()
    print("Expected training time:")
    print("  - GPU (RTX 3060/higher): 2-4 hours")
    print("  - GPU (GTX 1660/lower): 4-8 hours")
    print("  - CPU: 12-24 hours (NOT recommended)")
    print()
    
    choice = input("Start training now? (y/n): ").lower()
    
    if choice == 'y':
        print()
        print("Starting training...")
        print("="*70)
        
        # Import here to avoid issues if ultralytics not installed
        from ultralytics import YOLO
        
        # Load base model
        model = YOLO('yolov8n.pt')
        
        # Train
        results = model.train(
            data='VisDrone.yaml',
            epochs=50,
            imgsz=640,
            batch=16,
            name='visdrone_training'
        )
        
        print()
        print("="*70)
        print("✓ Training Complete!")
        print("="*70)
        print()
        print("Your trained model is at:")
        print("  runs/detect/visdrone_training/weights/best.pt")
        print()
        print("STEP 4: Use Your Trained Model")
        print("-" * 70)
        print()
        print("Copy the trained model:")
        print("  cp runs/detect/visdrone_training/weights/best.pt yolov8n-visdrone.pt")
        print()
        print("Then run your detection script:")
        print("  python yolov8_webcam.py")
        print()
        
        # Offer to copy automatically
        auto_copy = input("Automatically copy trained model? (y/n): ").lower()
        if auto_copy == 'y':
            import shutil
            src = 'runs/detect/visdrone_training/weights/best.pt'
            dst = 'yolov8n-visdrone.pt'
            
            if os.path.exists(dst):
                # Backup old model
                shutil.move(dst, dst + '.old')
                print(f"✓ Backed up old model to {dst}.old")
            
            shutil.copy(src, dst)
            print(f"✓ Copied trained model to {dst}")
            print()
            print("🎉 You're ready to run aerial detection!")
            print("   Run: python yolov8_webcam.py")
    else:
        print()
        print("Training cancelled. To train later, run:")
        print("  python train_visdrone.py")
        print()
        print("Or manually run:")
        print("  yolo detect train data=VisDrone.yaml model=yolov8n.pt epochs=50")
    
    print()
    print("="*70)


if __name__ == "__main__":
    main()
