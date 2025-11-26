package com.soc.ingestion.service;

import com.soc.ingestion.dto.EDRTelemetryRequest;
import com.soc.ingestion.dto.LogIngestionRequest;
import com.soc.ingestion.dto.NetFlowRequest;
import com.soc.ingestion.model.EDRTelemetry;
import com.soc.ingestion.model.NetFlowRecord;
import com.soc.ingestion.model.SecurityLog;
import com.soc.ingestion.repository.EDRTelemetryRepository;
import com.soc.ingestion.repository.NetFlowRepository;
import com.soc.ingestion.repository.LogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Multi-Modal Data Ingestion Service
 * Handles ingestion of different data types: Logs, NetFlow, and EDR Telemetry
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MultiModalIngestionService {
    
    private final LogRepository logRepository;
    private final NetFlowRepository netFlowRepository;
    private final EDRTelemetryRepository edrTelemetryRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final MLServiceClient mlServiceClient;
    
    private static final String LOG_TOPIC = "security-logs";
    private static final String NETFLOW_TOPIC = "netflow-records";
    private static final String EDR_TOPIC = "edr-telemetry";
    
    /**
     * Ingest security log (existing functionality)
     */
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
        securityLog.setDataType("LOG");
        
        SecurityLog savedLog = logRepository.save(securityLog);
        publishToKafka(LOG_TOPIC, savedLog.getId(), savedLog);
        triggerMLDetection(savedLog.getId(), "LOG", convertLogToMap(savedLog));
        
        return savedLog;
    }
    
    /**
     * Ingest NetFlow record
     */
    public NetFlowRecord ingestNetFlow(NetFlowRequest request) {
        log.info("Ingesting NetFlow record: {} -> {}:{}", 
                request.getSourceIp(), request.getDestinationIp(), request.getDestinationPort());
        
        NetFlowRecord record = new NetFlowRecord();
        record.setId(UUID.randomUUID().toString());
        record.setSourceIp(request.getSourceIp());
        record.setDestinationIp(request.getDestinationIp());
        record.setSourcePort(request.getSourcePort());
        record.setDestinationPort(request.getDestinationPort());
        record.setProtocol(request.getProtocol());
        record.setTimestamp(request.getTimestamp());
        record.setBytesSent(request.getBytesSent());
        record.setBytesReceived(request.getBytesReceived());
        record.setPacketsSent(request.getPacketsSent());
        record.setPacketsReceived(request.getPacketsReceived());
        record.setTcpFlags(request.getTcpFlags());
        record.setFlowDirection(request.getFlowDirection());
        record.setDeviceInterface(request.getDeviceInterface());
        record.setMetadata(request.getMetadata());
        record.setIngestedAt(LocalDateTime.now());
        record.setProcessed(false);
        record.setDataType("NETFLOW");
        
        NetFlowRecord savedRecord = netFlowRepository.save(record);
        publishToKafka(NETFLOW_TOPIC, savedRecord.getId(), savedRecord);
        triggerMLDetection(savedRecord.getId(), "NETFLOW", convertNetFlowToMap(savedRecord));
        
        return savedRecord;
    }
    
    /**
     * Ingest EDR telemetry
     */
    public EDRTelemetry ingestEDRTelemetry(EDRTelemetryRequest request) {
        log.info("Ingesting EDR telemetry from endpoint: {} - Event: {}", 
                request.getEndpointId(), request.getEventType());
        
        EDRTelemetry telemetry = new EDRTelemetry();
        telemetry.setId(UUID.randomUUID().toString());
        telemetry.setEndpointId(request.getEndpointId());
        telemetry.setHostname(request.getHostname());
        telemetry.setTimestamp(request.getTimestamp());
        telemetry.setEventType(request.getEventType());
        telemetry.setProcessName(request.getProcessName());
        telemetry.setProcessPath(request.getProcessPath());
        telemetry.setProcessHash(request.getProcessHash());
        telemetry.setProcessId(request.getProcessId());
        telemetry.setParentProcessId(request.getParentProcessId());
        telemetry.setParentProcessName(request.getParentProcessName());
        telemetry.setFilePath(request.getFilePath());
        telemetry.setFileHash(request.getFileHash());
        telemetry.setFileOperation(request.getFileOperation());
        telemetry.setRemoteIp(request.getRemoteIp());
        telemetry.setRemotePort(request.getRemotePort());
        telemetry.setConnectionDirection(request.getConnectionDirection());
        telemetry.setRegistryKey(request.getRegistryKey());
        telemetry.setRegistryValue(request.getRegistryValue());
        telemetry.setRegistryOperation(request.getRegistryOperation());
        telemetry.setUsername(request.getUsername());
        telemetry.setDomain(request.getDomain());
        telemetry.setSessionId(request.getSessionId());
        telemetry.setMetadata(request.getMetadata());
        telemetry.setIndicators(request.getIndicators());
        telemetry.setSeverity(request.getSeverity());
        telemetry.setIngestedAt(LocalDateTime.now());
        telemetry.setProcessed(false);
        telemetry.setDataType("EDR");
        
        EDRTelemetry savedTelemetry = edrTelemetryRepository.save(telemetry);
        publishToKafka(EDR_TOPIC, savedTelemetry.getId(), savedTelemetry);
        triggerMLDetection(savedTelemetry.getId(), "EDR", convertEDRToMap(savedTelemetry));
        
        return savedTelemetry;
    }
    
    /**
     * Publish data to Kafka topic
     */
    private void publishToKafka(String topic, String key, Object data) {
        try {
            kafkaTemplate.send(topic, key, data);
            log.info("Published {} to Kafka topic: {}", key, topic);
        } catch (Exception e) {
            log.error("Failed to publish to Kafka topic {}: {}", topic, e.getMessage());
        }
    }
    
    /**
     * Trigger ML detection with multi-modal data
     */
    private void triggerMLDetection(String id, String dataType, Map<String, Object> dataMap) {
        try {
            // Add data type to the map for multi-modal processing
            dataMap.put("dataType", dataType);
            dataMap.put("id", id);
            
            // Trigger direct detection asynchronously
            new Thread(() -> {
                try {
                    mlServiceClient.triggerDirectDetection(dataMap);
                } catch (Exception e) {
                    log.error("Error in direct detection thread: {}", e.getMessage());
                }
            }).start();
        } catch (Exception e) {
            log.error("Failed to trigger direct detection: {}", e.getMessage());
        }
    }
    
    /**
     * Convert SecurityLog to Map for ML processing
     */
    private Map<String, Object> convertLogToMap(SecurityLog log) {
        Map<String, Object> map = new HashMap<>();
        map.put("source", log.getSource());
        map.put("timestamp", log.getTimestamp() != null ? log.getTimestamp().toString() : LocalDateTime.now().toString());
        map.put("logLevel", log.getLogLevel());
        map.put("message", log.getMessage());
        map.put("metadata", log.getMetadata());
        return map;
    }
    
    /**
     * Convert NetFlowRecord to Map for ML processing
     */
    private Map<String, Object> convertNetFlowToMap(NetFlowRecord record) {
        Map<String, Object> map = new HashMap<>();
        map.put("sourceIp", record.getSourceIp());
        map.put("destinationIp", record.getDestinationIp());
        map.put("sourcePort", record.getSourcePort());
        map.put("destinationPort", record.getDestinationPort());
        map.put("protocol", record.getProtocol());
        map.put("timestamp", record.getTimestamp() != null ? record.getTimestamp().toString() : LocalDateTime.now().toString());
        map.put("bytesSent", record.getBytesSent());
        map.put("bytesReceived", record.getBytesReceived());
        map.put("packetsSent", record.getPacketsSent());
        map.put("packetsReceived", record.getPacketsReceived());
        map.put("tcpFlags", record.getTcpFlags());
        map.put("flowDirection", record.getFlowDirection());
        map.put("metadata", record.getMetadata());
        return map;
    }
    
    /**
     * Convert EDRTelemetry to Map for ML processing
     */
    private Map<String, Object> convertEDRToMap(EDRTelemetry telemetry) {
        Map<String, Object> map = new HashMap<>();
        map.put("endpointId", telemetry.getEndpointId());
        map.put("hostname", telemetry.getHostname());
        map.put("timestamp", telemetry.getTimestamp() != null ? telemetry.getTimestamp().toString() : LocalDateTime.now().toString());
        map.put("eventType", telemetry.getEventType());
        map.put("processName", telemetry.getProcessName());
        map.put("processPath", telemetry.getProcessPath());
        map.put("processHash", telemetry.getProcessHash());
        map.put("processId", telemetry.getProcessId());
        map.put("parentProcessId", telemetry.getParentProcessId());
        map.put("parentProcessName", telemetry.getParentProcessName());
        map.put("filePath", telemetry.getFilePath());
        map.put("fileHash", telemetry.getFileHash());
        map.put("fileOperation", telemetry.getFileOperation());
        map.put("remoteIp", telemetry.getRemoteIp());
        map.put("remotePort", telemetry.getRemotePort());
        map.put("connectionDirection", telemetry.getConnectionDirection());
        map.put("username", telemetry.getUsername());
        map.put("domain", telemetry.getDomain());
        map.put("severity", telemetry.getSeverity());
        map.put("indicators", telemetry.getIndicators());
        map.put("metadata", telemetry.getMetadata());
        return map;
    }
    
    /**
     * Get ingestion statistics across all data types
     */
    public Map<String, Long> getIngestionStats() {
        Map<String, Long> stats = new HashMap<>();
        stats.put("logs", logRepository.count());
        stats.put("netflow", netFlowRepository.count());
        stats.put("edr", edrTelemetryRepository.count());
        stats.put("total", logRepository.count() + netFlowRepository.count() + edrTelemetryRepository.count());
        return stats;
    }
}

