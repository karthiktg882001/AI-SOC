package com.soc.ingestion.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.Map;

@Document(collection = "security_logs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SecurityLog {
    @Id
    private String id;
    private String source;
    private LocalDateTime timestamp;
    private String logLevel;
    private String message;
    private Map<String, Object> metadata;
    private String rawLog;
    private LocalDateTime ingestedAt;
    private Boolean processed;
    private String dataType = "LOG"; // For multi-modal identification
}

