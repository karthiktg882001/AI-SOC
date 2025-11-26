# Share SOC Assistant with Your Friend

## 🎯 Your Current Setup

**Your Local IP Address:** `192.168.0.110`

**Frontend URL:** `http://192.168.0.110:3000`

---

## 📱 For Same Network Access (Easiest)

If your friend is on the **same Wi-Fi network**:

### Step 1: Allow Firewall Access

**Run PowerShell as Administrator** and execute:

```powershell
New-NetFirewallRule -DisplayName "SOC Assistant Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant ML Service" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant Log Ingestion" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### Step 2: Share This URL with Your Friend

```
http://192.168.0.110:3000
```

### Step 3: Share Login Credentials

**Option 1: Use existing account**
- Email: `test@gmail.com`
- Password: `Test@12345`

**Option 2: Create new account**
1. Login as admin: `admin@soc.local` / `Admin@12345`
2. Go to Admin Dashboard → User Management
3. Create a new user for your friend
4. Share the credentials

---

## 🌐 For Internet Access (Different Network)

If your friend is in a **different location**:

### Method 1: ngrok (Recommended for Testing)

**Step 1:** Install ngrok from https://ngrok.com/

**Step 2:** Make sure your app is running:
```powershell
docker-compose up -d
```

**Step 3:** Start ngrok tunnel:
```powershell
ngrok http 3000
```

**Step 4:** Share the ngrok HTTPS URL with your friend
- Example: `https://abc123.ngrok-free.app`
- This URL is temporary (changes when you restart ngrok)

### Method 2: Port Forwarding (Permanent)

**Step 1:** Find your public IP
- Visit: https://whatismyipaddress.com/
- Note your public IP (e.g., `203.0.113.45`)

**Step 2:** Configure router port forwarding
1. Access router admin: `http://192.168.1.1` (check router label)
2. Find "Port Forwarding" or "Virtual Server"
3. Forward port 3000 to `192.168.0.110`
4. Save settings

**Step 3:** Share public IP URL
```
http://YOUR_PUBLIC_IP:3000
```

**⚠️ Important:** Before exposing to internet:
- Change all default passwords
- Use strong passwords
- Consider using HTTPS

---

## ✅ Quick Test

**From your friend's device:**

1. Open browser
2. Go to: `http://192.168.0.110:3000`
3. Should see login page
4. Login with credentials

**If it doesn't work:**
- Check if both devices are on same network
- Check if firewall rules were added
- Check if Docker is running: `docker-compose ps`

---

## 🔐 Security Checklist

Before sharing access:

- [ ] Change default admin password
- [ ] Create separate user account for friend
- [ ] Use strong passwords
- [ ] For internet access: Use HTTPS
- [ ] Monitor access logs

---

## 📞 Quick Commands

**Check if services are running:**
```powershell
docker-compose ps
```

**Check your IP address:**
```powershell
ipconfig | findstr /i "IPv4"
```

**View logs if issues:**
```powershell
docker-compose logs frontend
docker-compose logs ml-service
```

**Restart services:**
```powershell
docker-compose restart
```

---

## 📚 More Information

- **Detailed Guide:** See `REMOTE_ACCESS_GUIDE.md`
- **Quick Reference:** See `QUICK_REMOTE_ACCESS.md`
- **Setup Script:** Run `scripts/setup_remote_access.ps1` as Administrator

---

## 🎉 That's It!

Your friend can now access the SOC Assistant at:
- **Same Network:** `http://192.168.0.110:3000`
- **Internet (ngrok):** Use the ngrok URL
- **Internet (Port Forward):** Use your public IP

Happy sharing! 🚀

