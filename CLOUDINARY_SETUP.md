## ☁️ Cloudinary Configuration Guide

### Why Cloudinary?
Render's free tier has **ephemeral storage** - files are deleted when the server restarts. Cloudinary provides **25GB free permanent cloud storage** for detection images/videos.

### Setup Steps

#### 1. Cloudinary Account (Already Done ✅)
Your credentials:
- Cloud Name: `dq9v0bo36`
- API Key: `895472581156914`  
- API Secret: `CjTNupJulkSZmSv7vaknaogJD1A`

#### 2. Set Environment Variable on Render

Go to your Render dashboard:
1. Navigate to: https://dashboard.render.com/
2. Click on **drone-aerial-view** service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add:
   ```
   Key: CLOUDINARY_API_SECRET
   Value: CjTNupJulkSZmSv7vaknaogJD1A
   ```
6. Click **Save Changes**

#### 3. Alternative: Use CLOUDINARY_URL (Simpler)

Instead of step 2, you can set single variable:
```
Key: CLOUDINARY_URL
Value: cloudinary://895472581156914:CjTNupJulkSZmSv7vaknaogJD1A@dq9v0bo36
```

This single URL contains all credentials and is easier to manage.

### How It Works

1. **Automatic Upload**: When detection occurs, image is uploaded to Cloudinary
2. **Permanent Storage**: Images persist even after server restarts
3. **Fast Delivery**: Cloudinary CDN delivers images globally
4. **Auto-Optimization**: Images are automatically optimized for web
5. **Fallback**: If Cloudinary fails, saves locally as backup

### Storage Stats

- **Free Tier**: 25GB storage + 25GB bandwidth/month
- **Current Usage**: 0.00 MB (just started)
- **Auto-Cleanup**: Old detections can be auto-deleted to save space

### View Your Uploads

Dashboard: https://console.cloudinary.com/console/c-dq9v0bo36/media_library/folders/campus-guardian

All detection images will be in: `campus-guardian/detections/`

### Test Locally

```bash
# Set environment variable
export CLOUDINARY_API_SECRET='CjTNupJulkSZmSv7vaknaogJD1A'

# Test upload
python test_cloudinary_upload.py
```

### Features

✅ Permanent cloud storage (no more lost images on restarts)  
✅ Auto-optimization for faster loading  
✅ CDN delivery (fast globally)  
✅ Automatic image compression  
✅ Max 1920x1080 resolution limit  
✅ Automatic format conversion (WebP, AVIF for modern browsers)  

### Next Steps

After setting the environment variable on Render:
1. Push code to GitHub
2. Render will auto-deploy
3. All new detections will be saved to Cloudinary permanently!

### Troubleshooting

**Images not uploading?**
- Check environment variable is set on Render
- View logs: `Render Dashboard → Logs`
- Look for "✅ Uploaded to Cloudinary" message

**Want to delete old images?**
```python
from cloudinary_storage import delete_image
delete_image('campus-guardian/detections/event_xxx_xxx')
```
