from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime, timedelta
import asyncio

from database import init_db, get_db
from models import Incident, IncidentReport, ThreatIntelligence
from services.anomaly_detector import AnomalyDetector
from services.generative_ai import GenerativeAIService
from services.kafka_consumer import KafkaConsumerService
from routers import incidents, dashboard, detection, device_info, auto_threat, protection, auth, system_info, direct_detection, log_reports, admin, chat, analyst, kpi
try:
    from routers import advanced
    ADVANCED_ROUTER_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Advanced router not available: {e}")
    ADVANCED_ROUTER_AVAILABLE = False

# Initialize services
anomaly_detector = AnomalyDetector()
generative_ai = GenerativeAIService()
kafka_consumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - simplified to ensure uvicorn stays running
    print("🚀 ML Service lifespan startup...", flush=True)
    try:
        init_db()
        print("✅ Database initialized", flush=True)
    except Exception as e:
        print(f"⚠️  Database init error (non-fatal): {e}", flush=True)
    
    global kafka_consumer
    kafka_consumer = None
    # Start Kafka consumer only if Kafka is available (graceful degradation)
    # Temporarily disabled to debug uvicorn binding issue
    # try:
    #     kafka_consumer = KafkaConsumerService(anomaly_detector)
    #     # Start consuming in background without blocking
    #     task = asyncio.create_task(kafka_consumer.start_consuming())
    #     # Don't await - let it run in background
    #     print("✅ Kafka consumer started", flush=True)
    # except Exception as e:
    #     print(f"⚠️  Kafka not available, running in standalone mode: {e}", flush=True)
    #     kafka_consumer = None
    print("ℹ️  Kafka consumer temporarily disabled for debugging", flush=True)
    
    print("✅ Lifespan startup complete - uvicorn should now be listening", flush=True)
    print("🌐 Uvicorn server should be accessible on http://0.0.0.0:8000", flush=True)
    try:
        yield
    except Exception as e:
        print(f"❌ Error in lifespan yield: {e}", flush=True)
        raise
    finally:
        print("🛑 Lifespan shutdown starting...", flush=True)
    # Shutdown
    print("🛑 Shutting down ML Service...", flush=True)
    if kafka_consumer:
        try:
            kafka_consumer.running = False
            if hasattr(kafka_consumer, 'consumer') and kafka_consumer.consumer:
                kafka_consumer.consumer.close()
        except Exception as e:
            print(f"⚠️  Error stopping Kafka consumer: {e}", flush=True)

app = FastAPI(
    title="SOC ML Service API",
    description="AI-Driven Security Operations Center ML Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(detection.router, prefix="/api/detect", tags=["Detection"])
app.include_router(device_info.router, prefix="/api/device", tags=["Device Info"])
app.include_router(auto_threat.router, prefix="/api/auto-threat", tags=["Auto Threat Detection"])
app.include_router(protection.router, prefix="/api/protection", tags=["Protection"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(system_info.router, prefix="/api/system", tags=["System Info"])
app.include_router(direct_detection.router, prefix="/api/direct", tags=["Direct Detection"])
app.include_router(log_reports.router, prefix="/api/log-reports", tags=["Log Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat Assistant"])
app.include_router(analyst.router, prefix="/api/analyst", tags=["Analyst"])
app.include_router(kpi.router, prefix="/api/kpi", tags=["KPI"])
if ADVANCED_ROUTER_AVAILABLE:
    app.include_router(advanced.router, prefix="/api/advanced", tags=["Advanced Features"])

# Add direct route for recent threats (for frontend compatibility)
from routers.dashboard import get_recent_threats
from database import get_db

@app.get("/api/threats/recent")
async def recent_threats(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent security threats - direct route for frontend"""
    return await get_recent_threats(limit=limit, db=db)

@app.get("/")
async def root():
    return {
        "message": "SOC ML Service API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "anomaly_detector": anomaly_detector.is_ready(),
            "generative_ai": generative_ai.is_ready()
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

