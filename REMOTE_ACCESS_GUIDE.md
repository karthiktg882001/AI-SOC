# Remote Access Guide - Share SOC Assistant with Friends

This guide explains how to give your friend access to the SOC Assistant application from anywhere.

## 📍 Option 1: Same Network (Local Network)

If your friend is on the **same Wi-Fi network** as you:

### Step 1: Find Your IP Address

**Windows (PowerShell):**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object IPAddress, InterfaceAlias
```

**Windows (Command Prompt):**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (Wi-Fi or Ethernet).

**Example:** `192.168.0.108` or `192.168.1.105`

### Step 2: Allow Firewall Access

Run PowerShell as **Administrator** and execute:

```powershell
# Allow frontend port
New-NetFirewallRule -DisplayName "SOC Assistant Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow

# Allow ML service port
New-NetFirewallRule -DisplayName "SOC Assistant ML Service" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Allow log ingestion port
New-NetFirewallRule -DisplayName "SOC Assistant Log Ingestion" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### Step 3: Share the URL

Give your friend this URL (replace with your actual IP):
```
http://YOUR_IP_ADDRESS:3000
```

**Example:** `http://192.168.0.108:3000`

### Step 4: Share Login Credentials

Create an account for your friend or share existing credentials:
- **Email:** `test@gmail.com`
- **Password:** `Test@12345`

Or create a new user account through the admin panel.

---

## 🌐 Option 2: Different Network (Internet Access)

If your friend is in a **different location** (different network/internet):

### Method A: Using ngrok (Easiest - Temporary Access)

**ngrok** creates a secure tunnel to your local server.

#### Step 1: Install ngrok

1. Go to https://ngrok.com/
2. Sign up for a free account
3. Download ngrok
4. Extract and add to PATH, or run from the folder

#### Step 2: Start Your Application

Make sure your Docker containers are running:
```powershell
docker-compose up -d
```

#### Step 3: Create ngrok Tunnel

```powershell
ngrok http 3000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

#### Step 4: Share the ngrok URL

Give your friend the **HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

**Note:** 
- Free ngrok URLs change each time you restart
- For permanent URLs, upgrade to a paid plan
- ngrok is great for testing and temporary access

#### Step 5: Update Frontend API URL (if needed)

If API calls fail, you may need to update the frontend environment:

1. Edit `docker-compose.yml`:
```yaml
frontend:
  environment:
    REACT_APP_API_URL: http://YOUR_IP:8000  # Use your public IP or ngrok URL
```

2. Rebuild:
```powershell
docker-compose up -d --build frontend
```

---

### Method B: Port Forwarding (Permanent Access)

This allows permanent access but requires router configuration.

#### Step 1: Find Your Public IP

Visit: https://whatismyipaddress.com/

**Note this IP address** (e.g., `203.0.113.45`)

#### Step 2: Configure Router Port Forwarding

1. **Access Router Admin Panel:**
   - Usually: `http://192.168.1.1` or `http://192.168.0.1`
   - Check router label for default IP/credentials

2. **Find Port Forwarding Section:**
   - Look for "Port Forwarding", "Virtual Server", or "NAT"
   - Different routers have different interfaces

3. **Add Port Forwarding Rules:**

   **Rule 1: Frontend (Port 3000)**
   - **Service Name:** SOC Frontend
   - **External Port:** 3000
   - **Internal Port:** 3000
   - **Internal IP:** Your computer's local IP (from Step 1 of Option 1)
   - **Protocol:** TCP

   **Rule 2: ML Service (Port 8000)**
   - **Service Name:** SOC ML Service
   - **External Port:** 8000
   - **Internal Port:** 8000
   - **Internal IP:** Your computer's local IP
   - **Protocol:** TCP

4. **Save and Apply**

#### Step 3: Update Firewall

Make sure Windows Firewall allows these ports (see Option 1, Step 2).

#### Step 4: Share Public IP

Give your friend:
```
http://YOUR_PUBLIC_IP:3000
```

**Example:** `http://203.0.113.45:3000`

#### Step 5: Security Warning ⚠️

**IMPORTANT:** Exposing your application to the internet has security risks:

1. **Change Default Passwords:**
   - Change admin password
   - Use strong passwords
   - Don't share admin credentials

2. **Use HTTPS:**
   - Set up SSL certificate
   - Use reverse proxy (Nginx with Let's Encrypt)

3. **Limit Access:**
   - Consider VPN instead
   - Use IP whitelisting if possible
   - Monitor access logs

---

### Method C: Cloud Deployment (Most Secure)

Deploy to a cloud service for permanent, secure access.

#### Option C1: Deploy to AWS/Azure/GCP

1. **Create Cloud Instance:**
   - AWS EC2, Azure VM, or Google Cloud Compute
   - Choose Ubuntu/Debian Linux

2. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

3. **Clone and Deploy:**
   ```bash
   git clone YOUR_REPO
   cd AISOC
   docker-compose up -d
   ```

4. **Configure Security Groups:**
   - Allow ports 3000, 8000, 8080
   - Restrict to specific IPs if possible

5. **Access via Public IP:**
   ```
   http://CLOUD_INSTANCE_IP:3000
   ```

#### Option C2: Deploy to Railway/Render/Fly.io

These platforms make deployment easier:

1. **Railway:**
   - Sign up at https://railway.app/
   - Connect GitHub repo
   - Deploy with one click

2. **Render:**
   - Sign up at https://render.com/
   - Create new Web Service
   - Connect repo and deploy

3. **Fly.io:**
   - Sign up at https://fly.io/
   - Use `fly launch` command
   - Automatic deployment

---

## 🔐 Security Best Practices

### For Local Network Access:
- ✅ Change default passwords
- ✅ Use strong passwords
- ✅ Limit to trusted users
- ✅ Monitor access logs

### For Internet Access:
- ✅ **Use HTTPS** (SSL certificate)
- ✅ **Change all default passwords**
- ✅ **Use strong, unique passwords**
- ✅ **Enable authentication**
- ✅ **Consider VPN** for better security
- ✅ **Regular security updates**
- ✅ **Monitor access logs**
- ✅ **Use firewall rules** to limit access

---

## 🧪 Testing Remote Access

### Test from Your Friend's Device:

1. **Check if port is open:**
   ```bash
   # From friend's device
   curl http://YOUR_IP:3000
   # Or
   telnet YOUR_IP 3000
   ```

2. **Test in browser:**
   - Open: `http://YOUR_IP:3000`
   - Should see login page

3. **Test API:**
   ```bash
   curl http://YOUR_IP:8000/api/dashboard/stats
   ```

---

## 🛠️ Troubleshooting

### Can't Access from Remote Location?

1. **Check Firewall:**
   - Windows Firewall must allow ports
   - Router firewall might block (check router settings)

2. **Check Docker Ports:**
   ```powershell
   docker-compose ps
   ```
   Should show ports bound to `0.0.0.0:3000->3000/tcp`

3. **Check Router Settings:**
   - Port forwarding configured correctly?
   - Internal IP is correct?
   - Router firewall allows connections?

4. **Check ISP:**
   - Some ISPs block incoming connections
   - May need to contact ISP

5. **Test Locally First:**
   - Can you access from another device on same network?
   - If yes, issue is with port forwarding/ISP
   - If no, check Docker and firewall

### Connection Timeout?

- Check if your IP address changed (dynamic IP)
- Verify port forwarding is still active
- Check if Docker containers are running

### API Calls Fail?

- Update `REACT_APP_API_URL` in `docker-compose.yml`
- Rebuild frontend: `docker-compose up -d --build frontend`
- Check CORS settings in nginx.conf

---

## 📝 Quick Reference

### Same Network:
```
http://YOUR_LOCAL_IP:3000
```

### Internet Access (Port Forwarding):
```
http://YOUR_PUBLIC_IP:3000
```

### Internet Access (ngrok):
```
https://YOUR_NGROK_URL.ngrok-free.app
```

### Cloud Deployment:
```
http://CLOUD_INSTANCE_IP:3000
```

---

## 💡 Recommendations

**For Testing/Demo:**
- Use **ngrok** (easiest, temporary)

**For Permanent Access (Same Location):**
- Use **same network** access

**For Permanent Access (Different Locations):**
- Use **cloud deployment** (most secure)
- Or **port forwarding** with HTTPS

**For Production:**
- **Always use HTTPS**
- **Deploy to cloud**
- **Use proper authentication**
- **Monitor and log access**

---

## 🆘 Need Help?

If you encounter issues:

1. Check Docker logs:
   ```powershell
   docker-compose logs frontend
   docker-compose logs ml-service
   ```

2. Check if services are running:
   ```powershell
   docker-compose ps
   ```

3. Verify network connectivity:
   ```powershell
   Test-NetConnection -ComputerName YOUR_IP -Port 3000
   ```

