# Build Instructions for AI SOC Assistant - Web Application

## Web Application Deployment

This application runs as a web application accessible through any modern web browser.

### Prerequisites
- Docker and Docker Compose installed
- Internet connection (for initial setup)

### Quick Start

1. **Start all services:**
```bash
docker-compose up --build
```

2. **Access the application:**
- Open your web browser
- Navigate to: `http://localhost:3000`

### Services

The application consists of:
- **Frontend** (React): Port 3000
- **ML Service** (FastAPI): Port 8000
- **Log Ingestion Service** (Spring Boot): Port 8080
- **MongoDB**: Port 27017
- **PostgreSQL**: Port 5432
- **Kafka**: Port 9092
- **Zookeeper**: Port 2181

### Access from Other Devices

To access from other devices on your network:

1. Find your computer's IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Linux/Mac: `ifconfig` or `ip addr`

2. Access from other devices:
   - `http://YOUR_IP_ADDRESS:3000`
   - Example: `http://192.168.1.100:3000`

### Production Deployment

For production deployment:

1. **Update environment variables** in `docker-compose.yml`
2. **Use a reverse proxy** (nginx) for HTTPS
3. **Configure domain name** pointing to your server
4. **Set up SSL certificates** for secure connections

### Features Available

- ✅ Real-time threat detection
- ✅ AI-powered security analysis
- ✅ Protection dashboard
- ✅ Incident management
- ✅ User profile and account management
- ✅ System information monitoring
- ✅ Device information tracking

### Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera
- Any modern browser with JavaScript enabled

### Mobile Access

The web application is fully responsive and works on:
- Mobile phones (iOS, Android)
- Tablets
- Desktop computers
- Any device with a web browser

No app installation required - just open in your browser!
