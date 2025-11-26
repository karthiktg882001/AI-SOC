package com.soc.ingestion.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * MongoDB model for NetFlow records
 */
@Document(collection = "netflow_records")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class NetFlowRecord {
    @Id
    private String id;
    private String sourceIp;
    private String destinationIp;
    private Integer sourcePort;
    private Integer destinationPort;
    private String protocol;
    private LocalDateTime timestamp;
    private Long bytesSent;
    private Long bytesReceived;
    private Long packetsSent;
    private Long packetsReceived;
    private Integer tcpFlags;
    private String flowDirection;
    private String deviceInterface;
    private Map<String, Object> metadata;
    private LocalDateTime ingestedAt;
    private Boolean processed;
    private String dataType = "NETFLOW"; // For multi-modal identification
}

