# Permanent Admin Account Setup

## ✅ Admin Account Created

A permanent admin account has been configured with the following credentials:

### **Admin Credentials:**
- **Name:** ADMIN
- **Email:** admin@soc.local
- **Password:** Admin@12345
- **Role:** admin
- **Status:** Active

---

## 🔧 How It Works

### **Automatic Creation/Update:**
The admin account is automatically created or updated every time the ML service starts:

1. **On Service Startup:** The `init_db()` function is called
2. **Check for Admin:** System checks if `admin@soc.local` exists
3. **Create or Update:**
   - If admin doesn't exist → Creates new admin account
   - If admin exists → Updates to ensure correct credentials
4. **Permanent Settings:**
   - Name: Always set to "ADMIN"
   - Password: Always set to "Admin@12345"
   - Role: Always set to "admin"
   - Status: Always active

### **Code Location:**
- File: `ml-service/database.py`
- Function: `init_db()`
- Called: On every service startup (in `main.py` lifespan)

---

## 🔐 Security Features

### **Password Encryption:**
- Password is encrypted using Fernet (reversible for admin viewing)
- Uses persistent encryption key from `docker-compose.yml`
- Password persists across container restarts

### **Account Protection:**
- Admin account cannot be deleted by other admins
- Admin account is always active
- Admin role cannot be removed

---

## 📋 Verification

### **Test Admin Login:**
```powershell
# PowerShell
$body = 'username=admin@soc.local&password=Admin@12345'
Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $body -ContentType 'application/x-www-form-urlencoded'
```

### **Expected Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@soc.local",
    "name": "ADMIN",
    "is_admin": true,
    "role": "admin"
  }
}
```

---

## 🔄 Persistence Guarantee

### **Why It's Permanent:**
1. **Automatic Recreation:** Admin account is created/updated on every service start
2. **Fixed Credentials:** Name and password are hardcoded (with env var override option)
3. **Database Persistence:** Account stored in PostgreSQL (persistent volume)
4. **No Deletion:** Admin account cannot be accidentally deleted

### **Environment Variables (Optional):**
You can override the default credentials via environment variables in `docker-compose.yml`:

```yaml
environment:
  ADMIN_PASSWORD: "YourCustomPassword"  # Default: Admin@12345
  ADMIN_NAME: "YourCustomName"          # Default: ADMIN
```

---

## 🚀 Usage

### **Login via Web Interface:**
1. Go to: http://localhost:3000/login
2. Email: `admin@soc.local`
3. Password: `Admin@12345`
4. Click "Login"

### **Login via API:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@soc.local&password=Admin@12345"
```

---

## ✅ Status

- ✅ Admin account created
- ✅ Login verified
- ✅ Password encrypted with persistent key
- ✅ Account persists across restarts
- ✅ Automatic recreation on service start

---

## 📝 Notes

- **Default Password:** `Admin@12345` (change in production!)
- **Email:** `admin@soc.local` (fixed, cannot be changed)
- **Name:** `ADMIN` (can be overridden via `ADMIN_NAME` env var)
- **Security:** For production, change the password via admin dashboard or set `ADMIN_PASSWORD` env var

---

**Last Updated:** 2024-11-22
**Status:** ✅ Active and Verified

