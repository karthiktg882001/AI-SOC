# Accessing SOC Assistant from Another Device

## Your Host Machine IP Address

**Primary IP (Wi-Fi):** `192.168.0.108`

This is the IP address other devices on your network should use to access the application.

## How to Access from Another Device

### Step 1: Ensure Both Devices are on the Same Network
- Both your host machine and the other device must be connected to the same Wi-Fi network

### Step 2: Access the Application
On the other device (phone, tablet, laptop), open a web browser and go to:

```
http://192.168.0.108:3000
```

### Step 3: Login
Use the credentials:
- **Email:** `test@gmail.com`
- **Password:** `Test@12345`

## Available Services

### Frontend (Web Application)
- **URL:** http://192.168.0.108:3000
- **Access:** Open in any web browser
- **Features:** Full SOC dashboard, incidents, reports, profile

### ML Service API (Direct Access)
- **URL:** http://192.168.0.108:8000
- **Use:** For API testing or direct API calls

### Log Ingestion API
- **URL:** http://192.168.0.108:8080
- **Use:** For sending security logs

## Troubleshooting

### Can't Access from Other Device?

1. **Check Firewall:**
   - Windows Firewall might be blocking port 3000
   - Allow port 3000 through Windows Firewall

2. **Verify Network:**
   - Ensure both devices are on the same network
   - Check if you can ping 192.168.0.108 from the other device

3. **Check Docker Ports:**
   ```powershell
   docker-compose ps
   ```
   - Should show `0.0.0.0:3000->3000/tcp`

4. **Test Connection:**
   - From the other device, try: `http://192.168.0.108:3000`

### Allow Port Through Windows Firewall

Run this command in PowerShell (as Administrator):
```powershell
New-NetFirewallRule -DisplayName "SOC Assistant Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant ML Service" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SOC Assistant Log Ingestion" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

## Mobile Device Access

### Android/iOS
1. Connect to the same Wi-Fi network
2. Open browser (Chrome, Safari, etc.)
3. Go to: `http://192.168.0.108:3000`
4. Login with your credentials

### Features Available on Mobile
- ✅ Full dashboard
- ✅ Real-time threat detection
- ✅ Incident management
- ✅ AI reports
- ✅ Profile management
- ✅ Theme switching

## Network Configuration

### Current Setup
- **Frontend:** Port 3000 (accessible from all network interfaces)
- **ML Service:** Port 8000 (accessible from all network interfaces)
- **Log Ingestion:** Port 8080 (accessible from all network interfaces)

### Port Binding
All services are bound to `0.0.0.0`, which means they accept connections from:
- Localhost (127.0.0.1)
- Local network (192.168.0.x)
- All network interfaces

## Security Note

⚠️ **Important:** The application is currently accessible from your local network. For production use:
- Change default passwords
- Use HTTPS
- Implement proper firewall rules
- Consider VPN access for remote connections

## Quick Test

From another device, test the connection:
```bash
# Test if port is accessible
curl http://192.168.0.108:3000

# Or open in browser
http://192.168.0.108:3000
```

## Finding Your IP Address

If your IP changes, find it again:
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object IPAddress, InterfaceAlias
```

Look for the IP address under "Wi-Fi" or "Ethernet" interface.

