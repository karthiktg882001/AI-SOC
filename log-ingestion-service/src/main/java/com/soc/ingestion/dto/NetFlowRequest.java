package com.soc.ingestion.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * DTO for NetFlow record ingestion
 * NetFlow provides network flow data including source/destination IPs, ports, protocols, and traffic statistics
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class NetFlowRequest {
    @NotBlank(message = "Source IP is required")
    private String sourceIp;
    
    @NotBlank(message = "Destination IP is required")
    private String destinationIp;
    
    @NotNull(message = "Source port is required")
    private Integer sourcePort;
    
    @NotNull(message = "Destination port is required")
    private Integer destinationPort;
    
    @NotBlank(message = "Protocol is required")
    private String protocol; // TCP, UDP, ICMP, etc.
    
    @NotNull(message = "Timestamp is required")
    private LocalDateTime timestamp;
    
    private Long bytesSent;
    private Long bytesReceived;
    private Long packetsSent;
    private Long packetsReceived;
    private Integer tcpFlags;
    private String flowDirection; // INBOUND, OUTBOUND, INTERNAL
    private String deviceInterface;
    private Map<String, Object> metadata; // Additional flow metadata
}

