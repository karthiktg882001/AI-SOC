from kafka import KafkaConsumer
import json
import os
from typing import Dict, Any
import asyncio
from database import SessionLocal
from models import Incident
from datetime import datetime
import uuid
from services.auto_threat_detector import AutoThreatDetector

class KafkaConsumerService:
    def __init__(self, anomaly_detector):
        self.anomaly_detector = anomaly_detector
        self.auto_threat_detector = AutoThreatDetector()  # Use enhanced auto threat detector
        self.consumer = None
        self.running = False
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = "security-logs"
    
    async def start_consuming(self):
        """Start consuming messages from Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='ml-service-group',
                consumer_timeout_ms=1000
            )
            self.running = True
            print(f"Started Kafka consumer for topic: {self.topic}")
            
            # Process messages in background
            asyncio.create_task(self._process_messages())
        except Exception as e:
            print(f"Error starting Kafka consumer: {e}")
            # Continue without Kafka if not available
            self.running = False
    
    async def _process_messages(self):
        """Process incoming Kafka messages"""
        if not self.consumer:
            return
        
        try:
            while self.running:
                try:
                    message_pack = self.consumer.poll(timeout_ms=1000)
                    if message_pack:
                        for topic_partition, messages in message_pack.items():
                            for message in messages:
                                log_data = message.value
                                await self._process_log(log_data)
                except Exception as e:
                    if "NoBrokersAvailable" in str(e) or "Connection" in str(e):
                        print(f"Kafka connection issue, retrying...: {e}")
                        await asyncio.sleep(5)
                    else:
                        print(f"Error processing Kafka message: {e}")
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in message processing loop: {e}")
    
    async def _process_log(self, log_data: Dict[str, Any]):
        """Process a single log entry with auto threat detection"""
        try:
            # Use auto threat detector with Deep Learning and Generative AI
            threat_result = self.auto_threat_detector.detect_threat_with_ai(log_data)
            
            if threat_result.get("threat_detected", False):
                # Incident already created by auto_threat_detector
                print(f"✅ Auto-detected {threat_result.get('threat_type', 'UNKNOWN')} threat (Severity: {threat_result.get('severity', 'MEDIUM')}, Zero-day: {threat_result.get('is_zero_day', False)})")
                print(f"   Incident ID: {threat_result.get('incident_id', 'N/A')}")
                ai_analysis = threat_result.get('ai_analysis', {})
                if isinstance(ai_analysis, dict):
                    summary = ai_analysis.get('ai_generated_summary', '')
                    if summary:
                        print(f"   AI Analysis: {summary[:100]}...")
                else:
                    print(f"   AI Analysis: Generated")
        except Exception as e:
            print(f"Error processing log with auto threat detector: {e}")
            # Fallback to basic anomaly detection
            try:
                is_anomaly, anomaly_score, threat_type = self.anomaly_detector.detect_anomaly(log_data)
                if is_anomaly:
                    db = SessionLocal()
                    try:
                        incident = Incident(
                            incident_id=str(uuid.uuid4()),
                            log_id=log_data.get("id"),
                            severity=self._determine_severity(anomaly_score),
                            status="OPEN",
                            threat_type=threat_type,
                            source_ip=log_data.get("metadata", {}).get("ip") or 
                                     log_data.get("metadata", {}).get("source_ip"),
                            destination_ip=log_data.get("metadata", {}).get("destination_ip"),
                            timestamp=datetime.fromisoformat(log_data.get("timestamp").replace("Z", "+00:00")) 
                                     if isinstance(log_data.get("timestamp"), str) else datetime.now(),
                            anomaly_score=anomaly_score,
                            description=log_data.get("message", ""),
                            raw_log_data=log_data
                        )
                        db.add(incident)
                        db.commit()
                        print(f"Created incident {incident.incident_id} for threat: {threat_type}")
                    except Exception as e2:
                        db.rollback()
                        print(f"Error creating incident: {e2}")
                    finally:
                        db.close()
            except Exception as e2:
                print(f"Error in fallback detection: {e2}")
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity based on anomaly score"""
        if score > 0.8:
            return "CRITICAL"
        elif score > 0.6:
            return "HIGH"
        elif score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            print("Kafka consumer stopped")

