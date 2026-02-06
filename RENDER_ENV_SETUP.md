## 🎯 Quick Deploy Guide - Set Environment Variable on Render

### Visual Step-by-Step

```
1. Open Browser → https://dashboard.render.com/
   
2. You'll see your services list:
   ┌─────────────────────────────────────┐
   │ ⚡ My Services                      │
   ├─────────────────────────────────────┤
   │ 🚀 drone-aerial-view    [CLICK ME] │ ← Click this
   │    Web Service                      │
   │    Last deployed: X minutes ago     │
   └─────────────────────────────────────┘

3. Left sidebar menu:
   ┌─────────────────┐
   │ Overview        │
   │ Logs            │
   │ Metrics         │
   │ Environment     │ ← Click this
   │ Settings        │
   │ Events          │
   └─────────────────┘

4. Environment Variables page:
   ┌────────────────────────────────────────────────┐
   │ Environment Variables                          │
   ├────────────────────────────────────────────────┤
   │                                                │
   │ Existing variables:                            │
   │ ✓ PYTHON_VERSION = 3.13.4                     │
   │ ✓ PORT = 8080                                 │
   │                                                │
   │ [+ Add Environment Variable]  ← Click this    │
   └────────────────────────────────────────────────┘

5. Fill in the form:
   ┌────────────────────────────────────────────────┐
   │ Add Environment Variable                       │
   ├────────────────────────────────────────────────┤
   │                                                │
   │ Key:   [CLOUDINARY_API_SECRET             ]   │
   │        ↑ Type exactly this                     │
   │                                                │
   │ Value: [CjTNupJulkSZmSv7vaknaogJD1A       ]   │
   │        ↑ Paste this (your API secret)          │
   │                                                │
   │        [ Cancel ]    [ Save Changes ]  ← Click │
   └────────────────────────────────────────────────┘

6. Confirmation:
   ┌────────────────────────────────────────────────┐
   │ ✅ Environment variable added                  │
   │                                                │
   │ Your service will redeploy automatically       │
   │ in a few moments...                            │
   └────────────────────────────────────────────────┘

7. Watch deployment:
   Click "Logs" tab to watch deployment progress
   
   You'll see:
   ┌────────────────────────────────────────────────┐
   │ Deployment Logs                                │
   ├────────────────────────────────────────────────┤
   │ ==> Downloading cache...                       │
   │ ==> Installing dependencies...                 │
   │ ==> Building...                                │
   │ ✅ Cloudinary configured successfully!         │
   │ 📦 Cloud: dq9v0bo36                            │
   │ ==> Starting server...                         │
   │ Your service is live 🎉                        │
   └────────────────────────────────────────────────┘

8. Done! 🎉
   Visit: https://drone-aerial-view.onrender.com/
```

---

### Copy-Paste Values

**Environment Variable Key** (copy exactly):
```
CLOUDINARY_API_SECRET
```

**Environment Variable Value** (copy exactly):
```
CjTNupJulkSZmSv7vaknaogJD1A
```

---

### Alternative: Use Single URL

Instead of the above, you can use one variable:

**Key**:
```
CLOUDINARY_URL
```

**Value**:
```
cloudinary://895472581156914:CjTNupJulkSZmSv7vaknaogJD1A@dq9v0bo36
```

This contains all credentials in one URL.

---

### Expected Timeline

```
00:00 - Click "Save Changes"
00:30 - Render detects new environment variable
01:00 - Build starts (installing dependencies)
02:30 - Build completes
03:00 - Service starts
03:30 - Service is LIVE ✅
```

**Total time**: ~3-4 minutes

---

### Verify It's Working

1. **Check Logs** (after deployment):
   ```
   ✅ Cloudinary configured successfully!
   📦 Cloud: dq9v0bo36
   ```

2. **Trigger a detection** (point camera at something)

3. **Look for upload confirmation**:
   ```
   ✅ Uploaded to Cloudinary: http://res.cloudinary.com/dq9v0bo36/...
   ```

4. **View uploaded image** in Cloudinary dashboard:
   https://console.cloudinary.com/console/c-dq9v0bo36/media_library/folders/campus-guardian

---

### Troubleshooting

**Variable not appearing after save?**
- Refresh the page
- It should appear in the list of environment variables

**Deployment not starting?**
- Go to **Manual Deploy** → **Deploy latest commit**

**Still not working?**
- Check logs for error messages
- Verify API secret has no extra spaces
- Make sure key is exactly: `CLOUDINARY_API_SECRET`

---

### What This Enables

✅ Permanent cloud storage for all detection images  
✅ Images survive server restarts (Render's free tier deletes local files)  
✅ CDN delivery for fast global access  
✅ Automatic image optimization  
✅ 25GB free storage (thousands of detections)  

---

**Ready?** Go to: https://dashboard.render.com/ and follow the steps above! 🚀
