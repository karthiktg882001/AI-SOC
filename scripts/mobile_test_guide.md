# Mobile Testing Guide

## Quick Setup for Mobile Device Testing

### Step 1: Find Your Computer's IP Address

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually WiFi or Ethernet)

**Mac/Linux:**
```bash
ifconfig | grep "inet "
# or
ip addr show
```

### Step 2: Ensure Devices Are on Same Network

- Your computer and mobile device must be on the same WiFi network
- Mobile data won't work - must use WiFi

### Step 3: Check Firewall Settings

**Windows:**
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Firewall"
3. Ensure "Docker Desktop" or allow port 3000, 8000, 8080

**Or temporarily disable firewall for testing:**
```powershell
# Run as Administrator
netsh advfirewall set allprofiles state off
```

### Step 4: Access from Mobile Device

1. Open browser on your phone/tablet
2. Navigate to: `http://YOUR_IP:3000`
   - Example: `http://192.168.1.100:3000`

### Step 5: Test Features

- [ ] Dashboard loads correctly
- [ ] Navigation works (tap Dashboard, Incidents)
- [ ] Charts display properly
- [ ] Touch interactions work
- [ ] No horizontal scrolling
- [ ] Text is readable
- [ ] Buttons are tappable

## Troubleshooting Mobile Access

### Can't Connect from Mobile:

1. **Check IP Address:**
   ```powershell
   ipconfig
   ```
   Make sure you're using the correct IP (not 127.0.0.1)

2. **Check Docker Port Binding:**
   ```bash
   docker-compose ps
   ```
   Should show: `0.0.0.0:3000->3000/tcp`

3. **Test from Computer First:**
   ```bash
   curl http://YOUR_IP:3000
   ```
   If this doesn't work, the issue is with your network/firewall

4. **Check Firewall:**
   - Windows Firewall might be blocking
   - Antivirus might be blocking
   - Router firewall might be blocking

5. **Try Different Port:**
   If port 3000 is blocked, you can change it in `docker-compose.yml`

## Alternative: Use ngrok for External Access

If same-network access doesn't work, use ngrok:

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com
   ```

2. **Expose localhost:3000:**
   ```bash
   ngrok http 3000
   ```

3. **Use the ngrok URL on mobile:**
   - ngrok provides a public URL like: `https://abc123.ngrok.io`
   - Access this from any device, anywhere

## Testing Checklist

### iPhone/iPad:
- [ ] Safari browser works
- [ ] Chrome browser works (if installed)
- [ ] Touch gestures work
- [ ] Portrait and landscape orientations

### Android:
- [ ] Chrome browser works
- [ ] Samsung Internet works
- [ ] Touch gestures work
- [ ] Portrait and landscape orientations

### Tablet:
- [ ] Larger screen displays correctly
- [ ] Touch interactions work
- [ ] Layout adapts to tablet size

## Network Speed Testing

Test on different network speeds:
- Fast WiFi (home/office)
- Slow WiFi
- 4G/5G mobile data (if using ngrok)

## Browser Testing on Mobile

Test in different mobile browsers:
- Safari (iOS)
- Chrome Mobile
- Firefox Mobile
- Samsung Internet
- Edge Mobile

