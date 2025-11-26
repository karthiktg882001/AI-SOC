# AI SOC Assistant - Testing Guide

## Quick Test

Run the automated test script:

```powershell
.\test-application.ps1
```

## Manual Testing Checklist

### 1. Service Health Check

- [ ] All Docker containers are running
- [ ] Frontend accessible at http://localhost:3000
- [ ] ML Service health check: http://localhost:8000/health
- [ ] API documentation: http://localhost:8000/docs

### 2. Authentication Testing

- [ ] **Login Page**

  - Navigate to http://localhost:3000
  - Should see login form
  - Test with invalid credentials (should show error)
  - Test with valid credentials:
    - Email: `admin@soc.local`
    - Password: `Admin@12345`
  - Should redirect to dashboard after successful login

- [ ] **Registration** (if available)

  - Test user registration
  - Verify email validation
  - Test password requirements

- [ ] **Logout**
  - Click logout button
  - Should clear session and return to login

### 3. Dashboard Testing

- [ ] **Overview Dashboard**

  - View statistics cards
  - Check real-time threat monitoring
  - Verify charts and graphs load
  - Test auto-refresh functionality

- [ ] **Incident Management**
  - View list of incidents
  - Filter by severity, status, date
  - Sort incidents
  - View incident details
  - Test incident status updates

### 4. Threat Detection Testing

- [ ] **Real-time Detection**

  - Check if new threats are detected
  - Verify threat severity classification
  - Test threat intelligence integration
  - Check XAI explanations (if available)

- [ ] **Manual Detection**
  - Submit log data for analysis
  - Verify detection results
  - Check AI-generated analysis

### 5. Advanced Features Testing

#### Explainable AI (XAI)

- [ ] View feature importance for detections
- [ ] Check SHAP explanations
- [ ] Verify explanation clarity

#### Threat Intelligence (TI)

- [ ] Check external TI integration
- [ ] Verify IP reputation checks
- [ ] Test TI data display in incidents

#### Graph Analysis

- [ ] View attack path visualization
- [ ] Check entity relationships
- [ ] Test compromised host tracking

#### Active Learning

- [ ] Submit analyst feedback
- [ ] Verify feedback processing
- [ ] Check model improvement stats

#### SOAR Automation

- [ ] Test automated response actions
- [ ] Verify playbook execution
- [ ] Check automation logs

### 6. API Testing

#### Using API Documentation

1. Visit http://localhost:8000/docs
2. Test endpoints interactively
3. Use "Authorize" button to set Bearer token

#### Using cURL/PowerShell

```powershell
# Login
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method POST -ContentType "application/x-www-form-urlencoded" `
    -Body "username=admin@soc.local&password=Admin@12345"

$token = $loginResponse.access_token

# Get Dashboard Stats
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/stats" -Headers $headers

# Get Incidents
Invoke-RestMethod -Uri "http://localhost:8000/api/incidents" -Headers $headers
```

### 7. Multi-Modal Data Ingestion

- [ ] Test log ingestion endpoint
- [ ] Submit NetFlow data
- [ ] Submit EDR telemetry
- [ ] Verify data storage in MongoDB

### 8. Performance Testing

- [ ] Test with multiple concurrent requests
- [ ] Check response times
- [ ] Verify database query performance
- [ ] Test Kafka message processing

### 9. Security Testing

- [ ] Verify authentication is required for protected endpoints
- [ ] Test JWT token expiration
- [ ] Check CORS configuration
- [ ] Verify password encryption
- [ ] Test role-based access control (RBAC)

### 10. Error Handling

- [ ] Test invalid API requests
- [ ] Verify error messages are clear
- [ ] Check error logging
- [ ] Test graceful degradation

## Test Data

### Sample Log Data for Testing

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "WARNING",
  "message": "Suspicious login attempt detected",
  "metadata": {
    "ip": "192.168.1.100",
    "user": "testuser",
    "source_ip": "10.0.0.1",
    "destination_ip": "192.168.1.50"
  }
}
```

### Test Credentials

- **Admin User:**
  - Email: `admin@soc.local`
  - Password: `Admin@12345`

## Common Issues & Solutions

### Issue: Services not starting

**Solution:**

```powershell
docker compose down
docker compose up -d
docker compose logs -f
```

### Issue: Login fails

**Solution:**

1. Check ML service is running: `docker ps`
2. Check ML service logs: `docker logs aisoc-ml-service-1`
3. Verify database is initialized
4. Check API connectivity: `curl http://localhost:8000/health`

### Issue: Frontend can't connect to API

**Solution:**

1. Check nginx configuration
2. Verify service names in docker-compose.yml
3. Check network connectivity: `docker network inspect aisoc_soc-network`

### Issue: Database connection errors

**Solution:**

1. Verify PostgreSQL is running
2. Check connection string in environment variables
3. Verify database schema is initialized

## Performance Benchmarks

Expected response times:

- Health check: < 100ms
- Login: < 500ms
- Dashboard stats: < 1s
- Incident list: < 2s
- Threat detection: < 3s

## Reporting Issues

When reporting issues, include:

1. Service logs: `docker compose logs [service-name]`
2. Error messages
3. Steps to reproduce
4. Expected vs actual behavior
5. Environment details (OS, Docker version, etc.)
