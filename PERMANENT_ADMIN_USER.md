# Permanent Admin User - Protected Account

## ✅ Permanent Admin User Configuration

A permanent admin user has been configured that **cannot be deleted or have critical fields modified**.

### **Account Credentials:**
- **Email:** `admin@soc.local`
- **Password:** `Admin@12345`
- **Name:** `Admin`
- **Role:** `admin`
- **Status:** `ACTIVE` (always)

---

## 🔒 Protection Features

### **1. Cannot Be Deleted**
- Any attempt to delete `admin@soc.local` will result in:
  ```
  Error 403: Cannot delete permanent admin user (admin@soc.local). 
  This is a protected system account.
  ```

### **2. Critical Fields Cannot Be Modified**
The following fields are **protected** and cannot be changed:
- ❌ **Email** - Cannot be changed from `admin@soc.local`
- ❌ **Admin Status** - Cannot remove admin privileges (`is_admin` must remain `True`)
- ❌ **Role** - Cannot be changed from `admin`
- ❌ **Active Status** - Cannot be deactivated (`is_active` must remain `True`)

### **3. Allowed Modifications**
The following field can be modified (for display purposes):
- ✅ **Name** - Can be changed (e.g., for display name customization)

---

## 🔄 Auto-Restoration

The permanent admin user is **automatically created/verified** on every service startup:

1. **On Service Start:**
   - Checks if `admin@soc.local` exists
   - If not found, creates it with default credentials
   - If found, ensures all protected fields are correct
   - Resets password to `Admin@12345` if changed

2. **Protection Enforcement:**
   - Even if someone tries to modify the account, it will be restored on next service restart
   - The account is always guaranteed to exist and be functional

---

## 📋 Implementation Details

### **Backend Protection (ml-service/routers/admin.py):**

#### **Delete Protection:**
```python
# Prevent deletion of permanent admin user
if user.email == "admin@soc.local":
    raise HTTPException(
        status_code=403, 
        detail="Cannot delete permanent admin user (admin@soc.local). 
                This is a protected system account."
    )
```

#### **Update Protection:**
```python
# Protect permanent admin user from critical changes
is_permanent_admin = user.email == "admin@soc.local"

if is_permanent_admin:
    # Prevent email change
    if user_data.email != "admin@soc.local":
        raise HTTPException(status_code=403, ...)
    
    # Prevent removing admin privileges
    if user_data.is_admin == False:
        raise HTTPException(status_code=403, ...)
    
    # Prevent role change
    if user_data.role != "admin":
        raise HTTPException(status_code=403, ...)
    
    # Prevent deactivation
    if user_data.is_active == False:
        raise HTTPException(status_code=403, ...)
```

### **Auto-Creation (ml-service/database.py):**
```python
def init_db():
    # ... create tables ...
    
    # Create/Update permanent admin user
    admin_email = "admin@soc.local"
    admin_password = "Admin@12345"
    admin_name = "Admin"
    
    admin_user = db.query(User).filter(User.email == admin_email).first()
    
    if not admin_user:
        # Create new permanent admin user
        admin_user = User(...)
        db.add(admin_user)
    else:
        # Ensure permanent admin user always has correct settings
        admin_user.name = admin_name
        admin_user.password_hash = get_password_hash(admin_password)
        admin_user.is_admin = True
        admin_user.role = "admin"
        admin_user.is_active = True
        # ... commit ...
```

---

## 🧪 Testing

### **Test 1: Login Verification**
```powershell
$body = 'username=admin@soc.local&password=Admin@12345'
Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $body -ContentType 'application/x-www-form-urlencoded'
```
**Expected:** Successful login with admin privileges

### **Test 2: Deletion Attempt**
```powershell
# Get admin token first
$token = "YOUR_ADMIN_TOKEN"

# Try to delete admin@soc.local
Invoke-RestMethod -Uri 'http://localhost:8000/api/admin/users/{user_id}' -Method DELETE -Headers @{Authorization="Bearer $token"}
```
**Expected:** Error 403 - Cannot delete permanent admin user

### **Test 3: Modification Attempt**
```powershell
# Try to change admin email
$body = @{email="newemail@example.com"} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/api/admin/users/{user_id}' -Method PUT -Body $body -Headers @{Authorization="Bearer $token"}
```
**Expected:** Error 403 - Cannot change email of permanent admin user

---

## ⚙️ Environment Variables (Optional)

You can override the default credentials via environment variables:

```yaml
# docker-compose.yml
ml-service:
  environment:
    ADMIN_PASSWORD: "YourCustomPassword@123"  # Optional
    ADMIN_NAME: "YourCustomName"              # Optional
```

**Note:** The email `admin@soc.local` is **fixed** and cannot be changed.

---

## 🔐 Security Notes

1. **Default Password:** The default password `Admin@12345` should be changed for production use via environment variable `ADMIN_PASSWORD`.

2. **Email Fixed:** The email `admin@soc.local` is hardcoded as the permanent admin identifier and cannot be changed.

3. **Auto-Restoration:** The account is automatically restored on service restart, ensuring it always exists even if someone attempts to modify it.

4. **Protection Level:** Protection is enforced at the API level, preventing both deletion and critical modifications.

---

## ✅ Status

- ✅ Permanent admin user created
- ✅ Deletion protection enabled
- ✅ Modification protection enabled
- ✅ Auto-restoration on startup enabled
- ✅ Login verified and working

**Last Updated:** 2024-11-22

