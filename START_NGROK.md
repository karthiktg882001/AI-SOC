# 🚀 Start ngrok - Share Your Application

## ✅ ngrok is Installed!

ngrok version 3.33.0 is ready to use.

---

## 📝 Next Steps

### Step 1: Get Your ngrok Authtoken

1. **Go to:** https://dashboard.ngrok.com/signup
2. **Sign up** with your email (free account)
3. **Copy your authtoken** from the dashboard
   - It looks like: `2abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

### Step 2: Authenticate ngrok

Run this command (replace with your actual authtoken):

```powershell
cd C:\Users\ACHARYS\Desktop\AISOC
.\ngrok.exe config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Step 3: Start the Tunnel

**Option A: Use the Script (Recommended)**
```powershell
cd C:\Users\ACHARYS\Desktop\AISOC
powershell -ExecutionPolicy Bypass -File scripts\start_ngrok.ps1
```

**Option B: Manual Start**
```powershell
cd C:\Users\ACHARYS\Desktop\AISOC
.\ngrok.exe http 3000
```

### Step 4: Share the URL

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

**Share this URL with your friend:**
```
https://abc123.ngrok-free.app
```

---

## 🎯 Quick Start (All-in-One)

If you already have your authtoken, run:

```powershell
cd C:\Users\ACHARYS\Desktop\AISOC

# Authenticate (replace with your authtoken)
.\ngrok.exe config add-authtoken YOUR_AUTHTOKEN

# Start tunnel
.\ngrok.exe http 3000
```

---

## 📱 What Your Friend Needs

1. **The ngrok HTTPS URL** (you'll get this when you start ngrok)
2. **Login credentials:**
   - Email: `test@gmail.com`
   - Password: `Test@12345`

---

## 🔍 View Requests

While ngrok is running, you can view all requests at:
```
http://127.0.0.1:4040
```

This shows:
- All incoming requests
- Request/response details
- Traffic inspection

---

## ⚠️ Important Notes

- **URL changes** each time you restart ngrok (free plan)
- **Session expires** after 2 hours of inactivity (free plan)
- **HTTPS is enabled** (secure connection)
- **Change passwords** before sharing!

---

## 🆘 Troubleshooting

**"not authenticated" error?**
- Get authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
- Run: `.\ngrok.exe config add-authtoken YOUR_AUTHTOKEN`

**"port 3000 in use"?**
- Make sure Docker is running: `docker-compose ps`
- Check if frontend is running: `docker-compose ps frontend`

**Connection refused?**
- Check Docker: `docker-compose ps`
- Restart services: `docker-compose restart`

---

## 📚 More Help

- **Full Guide:** See `NGROK_SETUP.md`
- **Remote Access:** See `REMOTE_ACCESS_GUIDE.md`
- **Quick Reference:** See `QUICK_REMOTE_ACCESS.md`

---

**Ready to share! Get your authtoken and start the tunnel! 🚀**

