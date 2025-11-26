# Admin Features & Standalone Services

## ✅ What's Been Implemented

### 1. Admin Role System
- Added `is_admin` and `role` fields to User model
- Default admin user created on startup:
  - **Email:** `admin@soc.local`
  - **Password:** `Admin@12345`
- Admin authentication middleware for protected routes

### 2. Admin Dashboard Features
- **Statistics Dashboard:**
  - Total users, active users, admin users
  - Total incidents, open incidents, resolved incidents

- **User Management:**
  - Create new users
  - View all users
  - Edit user details (name, email, role, status)
  - Delete users
  - Reset user passwords
  - Activate/deactivate users

- **Incident Management:**
  - View all incidents
  - Update incident status
  - Delete incidents

- **System Settings:**
  - System configuration (placeholder for future features)

### 3. Standalone Service Support
- **ML Service:**
  - Works independently without Kafka (graceful degradation)
  - Direct detection endpoint works even if Kafka is unavailable
  - Database initialization creates default admin user

- **Log Ingestion Service:**
  - Can work without Kafka (uses direct detection)
  - Falls back to direct ML service calls if Kafka fails

### 4. Frontend Admin Interface
- Admin dashboard route: `/admin`
- Admin link in navbar (only visible to admins)
- Protected admin routes with `AdminRoute` component
- Full CRUD operations for users and incidents

## 🔐 Admin Credentials

**Default Admin Account:**
- Email: `admin@soc.local`
- Password: `Admin@12345`

**Note:** Change the default password after first login!

## 🚀 How to Use

### 1. Rebuild Services
```bash
docker-compose up -d --build
```

### 2. Login as Admin
1. Go to http://localhost:3000/login
2. Enter admin credentials
3. You'll see the "🔐 Admin" link in the navbar

### 3. Access Admin Dashboard
- Click "🔐 Admin" in the navbar, or
- Go directly to http://localhost:3000/admin

### 4. Manage Users
- Create new users with admin or user roles
- Edit existing users
- Activate/deactivate accounts
- Delete users (cannot delete yourself)

### 5. Manage Incidents
- View all incidents
- Update incident status (Open, In Progress, Resolved, Closed)
- Delete incidents

## 📋 API Endpoints (Admin Only)

### User Management
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{id}` - Get user by ID
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `POST /api/admin/users/{id}/reset-password` - Reset user password

### Statistics
- `GET /api/admin/stats` - Get system statistics

### Incident Management
- `PUT /api/admin/incidents/{id}/status` - Update incident status
- `DELETE /api/admin/incidents/{id}` - Delete incident

### System Settings
- `GET /api/admin/settings` - Get system settings
- `GET /api/admin/logs` - Get system logs (placeholder)

## 🔒 Security Features

1. **Admin-Only Routes:**
   - All `/api/admin/*` endpoints require admin authentication
   - Frontend admin routes protected by `AdminRoute` component

2. **Self-Protection:**
   - Admins cannot deactivate their own account
   - Admins cannot delete their own account

3. **Role-Based Access:**
   - Users have roles: `user`, `admin`, `analyst`
   - Admin routes check both `is_admin` flag and `role` field

## 🛠️ Standalone Operation

### ML Service Standalone
- Works without Kafka (logs warning but continues)
- Direct detection endpoint always available
- Database operations work independently

### Log Ingestion Standalone
- Saves logs to MongoDB
- Attempts Kafka publish (fails gracefully if unavailable)
- Always sends to ML service direct detection

## 📝 Database Schema Updates

```sql
-- Users table now includes:
is_admin BOOLEAN DEFAULT FALSE
role VARCHAR(50) DEFAULT 'user'
```

## 🎯 Next Steps

1. **Change Default Admin Password:**
   - Login as admin
   - Go to Profile → Change Password

2. **Create Additional Admins:**
   - Use admin dashboard to create more admin users

3. **Configure System Settings:**
   - Access Settings tab in admin dashboard

4. **Monitor System:**
   - Check Statistics tab regularly
   - Review incident management

## ⚠️ Important Notes

- Default admin password should be changed immediately
- Services work independently but perform better with all services running
- Admin dashboard is only accessible to users with `is_admin=true` or `role='admin'`
- All admin operations are logged (can be extended for audit trail)

