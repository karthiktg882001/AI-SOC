# Ngrok Setup Guide

## Step 1: Install Ngrok

### Windows:

1. Download ngrok from https://ngrok.com/download
2. Extract the zip file
3. Add ngrok.exe to your PATH or place it in a folder accessible from command line

### Or use Chocolatey:

```powershell
choco install ngrok
```

### Or use Scoop:

```powershell
scoop install ngrok
```

## Step 2: Get Your Auth Token

1. Sign up at https://dashboard.ngrok.com/signup (free account)
2. Go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken

## Step 3: Configure Ngrok

1. Run this command to set your authtoken:

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

Or edit `ngrok.yml` and add your authtoken:

```yaml
authtoken: YOUR_AUTH_TOKEN_HERE
```

## Step 4: Start Ngrok Tunnels

### Option 1: Tunnel Frontend Only (Recommended)

This tunnels the frontend on port 3000, which proxies all API calls:

```powershell
ngrok http 3000
```

### Option 2: Use Configuration File

```powershell
ngrok start --config ngrok.yml frontend
```

### Option 3: Multiple Tunnels

```powershell
ngrok start --config ngrok.yml --all
```

## Step 5: Access Your Application

After starting ngrok, you'll see output like:

```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

Open the HTTPS URL in your browser to access your SOC Assistant application.

## Important Notes

1. **Free ngrok accounts** have limitations:

   - Random subdomain each time you restart
   - Limited connections per minute
   - Session timeout after inactivity

2. **For production**, consider:

   - Paid ngrok plan for static domains
   - Or use other tunneling services (localtunnel, cloudflared, etc.)

3. **Security**: The ngrok URL will be publicly accessible. Make sure:
   - Your application has proper authentication
   - Don't expose sensitive data
   - Consider using ngrok's IP restrictions

## Troubleshooting

- If port 3000 is not accessible, make sure Docker containers are running:

  ```powershell
  docker compose ps
  ```

- If you get "authtoken required", make sure you've set your authtoken:

  ```powershell
  ngrok config add-authtoken YOUR_TOKEN
  ```

- To see ngrok web interface, visit: http://localhost:4040
