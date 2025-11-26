# MongoDB Atlas Configuration

## ✅ MongoDB Atlas Connection Configured

The application has been configured to use MongoDB Atlas cloud database instead of local MongoDB.

### **Connection Details:**
- **Connection String:** `mongodb+srv://admin:Admin@12345@cluster0.9vyfwgw.mongodb.net/soc_logs`
- **Database:** `soc_logs`
- **Cluster:** `cluster0.9vyfwgw.mongodb.net`

---

## ⚠️ Important: MongoDB Atlas Setup Requirements

### **1. IP Whitelisting (Required)**
MongoDB Atlas requires IP addresses to be whitelisted for security.

**Option A: Whitelist All IPs (For Testing)**
1. Go to MongoDB Atlas Dashboard
2. Network Access → Add IP Address
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
4. Save

**Option B: Whitelist Specific IPs (Recommended for Production)**
1. Find your server's public IP
2. Go to Network Access → Add IP Address
3. Add your IP address
4. Save

**For Docker Containers:**
- If running locally, whitelist your public IP
- If running on a server, whitelist the server's public IP
- For ngrok, you may need to whitelist ngrok's IP ranges

### **2. Database User Permissions**
Ensure the database user has proper permissions:
- **Username:** `admin`
- **Password:** `Admin@12345`
- **Database:** `soc_logs`
- **Permissions:** Read/Write access to `soc_logs` database

### **3. Connection String Format**
The connection string is URL-encoded:
- Password `Admin@12345` is encoded as `Admin%4012345` (where `%40` = `@`)

---

## 🔧 Configuration Files Updated

### **docker-compose.yml**
```yaml
ml-service:
  environment:
    MONGODB_URI: mongodb+srv://admin:Admin%4012345@cluster0.9vyfwgw.mongodb.net/soc_logs?retryWrites=true&w=majority&appName=Cluster0

log-ingestion-service:
  environment:
    MONGODB_URI: mongodb+srv://admin:Admin%4012345@cluster0.9vyfwgw.mongodb.net/soc_logs?retryWrites=true&w=majority&appName=Cluster0
```

### **Connection Parameters:**
- `retryWrites=true` - Enable retryable writes
- `w=majority` - Write concern (majority of replica set)
- `appName=Cluster0` - Application name for monitoring

---

## 🚀 Testing the Connection

### **Test Log Ingestion:**
```powershell
$body = @{
    source = 'test'
    timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    logLevel = 'INFO'
    message = 'Testing MongoDB Atlas connection'
    metadata = @{}
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri 'http://localhost:8080/api/logs/ingest' -Method POST -Body $body -ContentType 'application/json'
```

### **Check Service Logs:**
```bash
docker logs aisoc-log-ingestion-service-1 --tail 50
docker logs aisoc-ml-service-1 --tail 50
```

---

## 🔍 Troubleshooting

### **SSL/TLS Errors:**
If you see SSL errors:
1. **Check IP Whitelisting:** Ensure your IP is whitelisted in MongoDB Atlas
2. **Check Network:** Ensure Docker container can reach the internet
3. **Check Credentials:** Verify username and password are correct
4. **Check Database Name:** Ensure `soc_logs` database exists in Atlas

### **Connection Timeout:**
- **Firewall:** Check if firewall is blocking outbound connections
- **Network:** Ensure Docker has internet access
- **Atlas Status:** Check MongoDB Atlas cluster status

### **Authentication Errors:**
- Verify username and password in MongoDB Atlas
- Check database user permissions
- Ensure password is URL-encoded correctly (`@` = `%40`)

---

## 📋 MongoDB Atlas Dashboard

### **Monitor Connection:**
1. Go to MongoDB Atlas Dashboard
2. Clusters → Your Cluster
3. Metrics → Check connection metrics
4. Logs → View connection logs

### **Database Collections:**
After successful connection, you should see:
- `security_logs` collection (created automatically)
- Logs stored with timestamps and metadata

---

## 🔄 Fallback to Local MongoDB

If you need to switch back to local MongoDB:

1. **Update docker-compose.yml:**
```yaml
MONGODB_URI: mongodb://admin:admin123@mongodb:27017/soc_logs?authSource=admin
```

2. **Add mongodb dependency:**
```yaml
depends_on:
  - mongodb
```

3. **Restart services:**
```bash
docker-compose up -d ml-service log-ingestion-service
```

---

## ✅ Verification Checklist

- [ ] MongoDB Atlas cluster is running
- [ ] IP address is whitelisted in Atlas
- [ ] Database user `admin` exists with correct password
- [ ] Database `soc_logs` exists (or will be created automatically)
- [ ] Connection string is correctly URL-encoded
- [ ] Services can reach the internet
- [ ] Test log ingestion succeeds

---

**Status:** ⚠️ Configuration Updated - Requires IP Whitelisting in MongoDB Atlas
**Last Updated:** 2024-11-22

