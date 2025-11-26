package com.soc.ingestion.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * MongoDB model for EDR telemetry records
 */
@Document(collection = "edr_telemetry")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class EDRTelemetry {
    @Id
    private String id;
    private String endpointId;
    private String hostname;
    private LocalDateTime timestamp;
    private String eventType;
    private String processName;
    private String processPath;
    private String processHash;
    private Integer processId;
    private Integer parentProcessId;
    private String parentProcessName;
    private String filePath;
    private String fileHash;
    private String fileOperation;
    private String remoteIp;
    private Integer remotePort;
    private String connectionDirection;
    private String registryKey;
    private String registryValue;
    private String registryOperation;
    private String username;
    private String domain;
    private String sessionId;
    private Map<String, Object> metadata;
    private List<String> indicators;
    private String severity;
    private LocalDateTime ingestedAt;
    private Boolean processed;
    private String dataType = "EDR"; // For multi-modal identification
}

