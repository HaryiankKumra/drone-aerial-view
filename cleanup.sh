#!/bin/bash

echo "🧹 Cleaning up project structure..."
echo "⚠️  Note: Essential files (storage.py, cloudinary_storage.py, config.py, csv_logger.py) are KEPT"

# Delete old documentation
echo "Deleting old documentation..."
rm -f CAMERA_FIX.md
rm -f CLOUDINARY_SETUP.md
rm -f DEPLOYMENT.md
rm -f FIXES_SUMMARY.md
rm -f LOCAL_TESTING.md
rm -f MONGODB_SETUP.md
rm -f PHASE2_SETUP.md
rm -f PROJECT_DOCUMENTATION.md
rm -f RASPBERRY_PI_SETUP.md
rm -f RENDER_ENV_SETUP.md

# Delete training scripts
echo "Deleting training scripts..."
rm -f auto_train.py
rm -f train_now.py
rm -f train_visdrone.py

# Delete test files
echo "Deleting test files..."
rm -f test_api_client.py
rm -f test_cloudinary_upload.py
rm -f test_real_upload.py

# Delete unused modules (KEEP storage.py, cloudinary_storage.py, config.py, csv_logger.py - they are needed!)
echo "Deleting unused modules..."
rm -f imgur_storage.py
rm -f database.py
rm -f yolov8_webcam.py

# Delete old models (KEEP yolov8n-visdrone.pt - it's the current model!)
echo "Deleting old models..."
rm -f yolov8s-visdrone.pt
rm -f yolov8s-visdrone.pt.backup
rm -f yolov8s.pt

# Delete duplicate venv and training folders
echo "Deleting duplicate folders..."
rm -rf venv
rm -rf datasets
rm -rf runs

# Delete misc files
echo "Deleting misc files..."
rm -f last_upload_url.txt

echo "✅ Cleanup completed successfully!"
echo "📁 Essential files preserved:"
echo "   - storage.py (detection event storage)"
echo "   - cloudinary_storage.py (image upload)"
echo "   - config.py (model configuration)"
echo "   - csv_logger.py (event logging)"
echo "   - yolov8n-visdrone.pt (current YOLO model)"
