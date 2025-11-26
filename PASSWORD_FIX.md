# Password Persistence Fix

## ✅ Issue Fixed

**Problem:** User passwords were getting reset to "No password set" after container restarts (typically after 1 day or when services restart).

**Root Cause:** The `PASSWORD_ENCRYPTION_KEY` was not set in `docker-compose.yml`, causing the system to generate a new encryption key every time the container restarted. This made all previously encrypted passwords unreadable.

## 🔧 Solution Applied

### 1. Added Persistent Encryption Key
- Generated a persistent Fernet encryption key: `lyDnXCe1rz37a0ZNTS-96nUuvzqFVytSnwUaBxWT9e8=`
- Added `PASSWORD_ENCRYPTION_KEY` environment variable to `docker-compose.yml`
- Added `SECRET_KEY` for JWT token security

### 2. Improved Error Handling
- Updated `decrypt_password()` function to detect encryption key mismatches
- Added special marker `[ENCRYPTION_KEY_MISMATCH]` for key mismatch detection
- Updated admin dashboard to show `[Password reset required]` for passwords encrypted with old keys

### 3. Files Modified
- `docker-compose.yml` - Added persistent encryption keys
- `ml-service/routers/auth.py` - Improved decryption error handling
- `ml-service/routers/admin.py` - Better password display for key mismatches

## 📋 What This Means

### For Existing Users
- **Passwords encrypted with the OLD key:** Will show as `[Password reset required]` in admin panel
- **Action Required:** Admin needs to reset these passwords using the "Change Password" feature
- **Users can still login:** If they remember their password, login will work (uses backward-compatible verification)

### For New Users
- **All new passwords:** Will be encrypted with the persistent key
- **No more resets:** Passwords will persist across container restarts
- **Long-term stability:** Passwords will remain valid indefinitely

## 🔄 Migration Steps (For Admins)

If you see users with `[Password reset required]`:

1. Go to Admin Dashboard → Users
2. Click "Edit" on the user
3. Enter a new password in the "Change Password" section
4. Save the changes
5. The new password will be encrypted with the persistent key

## 🔒 Security Notes

- **Encryption Key:** Stored in `docker-compose.yml` (consider using Docker secrets for production)
- **Key Rotation:** If you need to rotate the key, all users will need to reset passwords
- **Production:** Use environment variables or secrets management for the encryption key

## ✅ Verification

To verify the fix is working:

1. **Check service is running:**
   ```bash
   docker-compose ps ml-service
   ```

2. **Check logs for key loading:**
   ```bash
   docker logs aisoc-ml-service-1 | grep -i "encryption\|key"
   ```

3. **Test password persistence:**
   - Create a new user or change a password
   - Restart the container: `docker-compose restart ml-service`
   - Verify the password still works

## 📝 Technical Details

### Encryption Method
- **Algorithm:** Fernet (symmetric encryption)
- **Purpose:** Reversible encryption for admin password viewing
- **Key Format:** Base64-encoded 32-byte key

### Backward Compatibility
- System still supports old bcrypt-hashed passwords
- Login verification tries decryption first, then falls back to bcrypt
- Old passwords continue to work for login

---

**Status:** ✅ Fixed and Deployed
**Date:** 2024-11-22
**Service:** ML Service (Port 8000)

