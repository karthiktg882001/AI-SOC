# Quick Guide: Share SOC Assistant with Your Friend

## 🚀 Quick Start (Same Network)

If your friend is on the **same Wi-Fi network**:

### Step 1: Find Your IP Address

**Windows PowerShell:**
```powershell
ipconfig
```
Look for "IPv4 Address" (usually starts with 192.168.x.x)

**Or use this command:**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object IPAddress
```

### Step 2: Allow Firewall (Run as Administrator)

Open PowerShell **as Administrator** and run:
```powershell
New-NetFirewallRule -DisplayName "SOC Assistant Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant ML Service" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant Log Ingestion" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### Step 3: Share the URL

Give your friend this URL (replace with your IP):
```
http://YOUR_IP_ADDRESS:3000
```

**Example:** `http://192.168.0.108:3000`

### Step 4: Share Login

- **Email:** `test@gmail.com`
- **Password:** `Test@12345`

Or create a new account for them via Admin panel.

---

## 🌐 Internet Access (Different Network)

### Option A: ngrok (Easiest - Temporary)

1. **Install ngrok:**
   - Go to https://ngrok.com/
   - Sign up (free)
   - Download and extract

2. **Start your app:**
   ```powershell
   docker-compose up -d
   ```

3. **Create tunnel:**
   ```powershell
   ngrok http 3000
   ```

4. **Share the ngrok URL:**
   - You'll see: `https://abc123.ngrok-free.app`
   - Share this with your friend

**Note:** URL changes each time you restart ngrok.

---

### Option B: Port Forwarding (Permanent)

1. **Find your public IP:**
   - Visit: https://whatismyipaddress.com/
   - Note your IP (e.g., `203.0.113.45`)

2. **Configure router:**
   - Access router: `http://192.168.1.1` (check router label)
   - Find "Port Forwarding" section
   - Forward port 3000 to your computer's local IP
   - Save settings

3. **Share public IP:**
   ```
   http://YOUR_PUBLIC_IP:3000
   ```

**⚠️ Security Warning:** Change passwords before exposing to internet!

---

## 📋 Quick Checklist

- [ ] Docker containers running (`docker-compose ps`)
- [ ] Firewall allows port 3000
- [ ] Friend has your IP address
- [ ] Friend can access `http://YOUR_IP:3000`
- [ ] Login credentials shared

---

## 🆘 Troubleshooting

**Can't access?**
1. Check firewall: Run setup script as admin
2. Check Docker: `docker-compose ps` (should show running)
3. Check IP: Make sure you're using the correct IP
4. Test locally: Try `http://localhost:3000` first

**Need more help?**
- See `REMOTE_ACCESS_GUIDE.md` for detailed instructions
- Run `scripts/setup_remote_access.ps1` as Administrator

---

## 🔐 Security Reminder

- ✅ Change default passwords
- ✅ Use strong passwords
- ✅ For internet access, use HTTPS
- ✅ Consider VPN for better security

