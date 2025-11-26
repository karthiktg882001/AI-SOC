package com.soc.ingestion.repository;

import com.soc.ingestion.model.EDRTelemetry;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EDRTelemetryRepository extends MongoRepository<EDRTelemetry, String> {
    List<EDRTelemetry> findByEndpointId(String endpointId);
    List<EDRTelemetry> findByHostname(String hostname);
    List<EDRTelemetry> findByEventType(String eventType);
    List<EDRTelemetry> findByTimestampBetween(LocalDateTime start, LocalDateTime end);
    List<EDRTelemetry> findByProcessHash(String processHash);
    List<EDRTelemetry> findBySeverity(String severity);
}

