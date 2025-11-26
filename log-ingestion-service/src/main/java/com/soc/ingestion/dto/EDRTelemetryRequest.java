package com.soc.ingestion.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * DTO for EDR (Endpoint Detection and Response) telemetry ingestion
 * EDR provides endpoint-level security data including process activity, file operations, and registry changes
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class EDRTelemetryRequest {
    @NotBlank(message = "Endpoint ID is required")
    private String endpointId;
    
    @NotBlank(message = "Hostname is required")
    private String hostname;
    
    @NotNull(message = "Timestamp is required")
    private LocalDateTime timestamp;
    
    @NotBlank(message = "Event type is required")
    private String eventType; // PROCESS_CREATE, FILE_WRITE, REGISTRY_MODIFY, NETWORK_CONNECT, etc.
    
    private String processName;
    private String processPath;
    private String processHash; // SHA256 hash
    private Integer processId;
    private Integer parentProcessId;
    private String parentProcessName;
    
    // File operations
    private String filePath;
    private String fileHash;
    private String fileOperation; // CREATE, WRITE, DELETE, READ
    
    // Network connections
    private String remoteIp;
    private Integer remotePort;
    private String connectionDirection; // INBOUND, OUTBOUND
    
    // Registry operations
    private String registryKey;
    private String registryValue;
    private String registryOperation; // CREATE, MODIFY, DELETE
    
    // User context
    private String username;
    private String domain;
    private String sessionId;
    
    // Additional telemetry
    private Map<String, Object> metadata;
    private List<String> indicators; // IOCs detected
    private String severity; // LOW, MEDIUM, HIGH, CRITICAL
}

