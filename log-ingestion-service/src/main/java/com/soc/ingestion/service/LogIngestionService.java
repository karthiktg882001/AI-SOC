package com.soc.ingestion.service;

import com.soc.ingestion.dto.LogIngestionRequest;
import com.soc.ingestion.model.SecurityLog;
import com.soc.ingestion.repository.LogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class LogIngestionService {
    
    private final LogRepository logRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final MLServiceClient mlServiceClient;
    private static final String LOG_TOPIC = "security-logs";
    
    public SecurityLog ingestLog(LogIngestionRequest request) {
        log.info("Ingesting log from source: {}", request.getSource());
        
        SecurityLog securityLog = new SecurityLog();
        securityLog.setId(UUID.randomUUID().toString());
        securityLog.setSource(request.getSource());
        securityLog.setTimestamp(request.getTimestamp());
        securityLog.setLogLevel(request.getLogLevel());
        securityLog.setMessage(request.getMessage());
        securityLog.setMetadata(request.getMetadata());
        securityLog.setRawLog(request.getRawLog());
        securityLog.setIngestedAt(LocalDateTime.now());
        securityLog.setProcessed(false);
        
        // Save to MongoDB
        SecurityLog savedLog = logRepository.save(securityLog);
        
        // Publish to Kafka for real-time processing
        try {
            kafkaTemplate.send(LOG_TOPIC, savedLog.getId(), savedLog);
            log.info("Published log {} to Kafka topic: {}", savedLog.getId(), LOG_TOPIC);
        } catch (Exception e) {
            log.error("Failed to publish log to Kafka: {}", e.getMessage());
        }
        
        // Also trigger direct detection (works even if Kafka is down)
        try {
            Map<String, Object> logData = new HashMap<>();
            logData.put("id", savedLog.getId());
            logData.put("source", savedLog.getSource());
            logData.put("timestamp", savedLog.getTimestamp() != null ? savedLog.getTimestamp().toString() : LocalDateTime.now().toString());
            logData.put("logLevel", savedLog.getLogLevel());
            logData.put("message", savedLog.getMessage());
            logData.put("metadata", savedLog.getMetadata());
            
            // Trigger direct detection asynchronously
            new Thread(() -> {
                try {
                    mlServiceClient.triggerDirectDetection(logData);
                } catch (Exception e) {
                    log.error("Error in direct detection thread: {}", e.getMessage());
                }
            }).start();
        } catch (Exception e) {
            log.error("Failed to trigger direct detection: {}", e.getMessage());
        }
        
        return savedLog;
    }
    
    public long getIngestionStats() {
        return logRepository.count();
    }
}

