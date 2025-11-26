package com.soc.ingestion.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LogIngestionRequest {
    @NotBlank(message = "Source is required")
    private String source;
    
    @NotNull(message = "Timestamp is required")
    private LocalDateTime timestamp;
    
    @NotBlank(message = "Log level is required")
    private String logLevel;
    
    @NotBlank(message = "Message is required")
    private String message;
    
    private Map<String, Object> metadata;
    private String rawLog;
}

