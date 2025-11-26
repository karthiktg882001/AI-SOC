package com.soc.ingestion.controller;

import com.soc.ingestion.dto.EDRTelemetryRequest;
import com.soc.ingestion.dto.LogIngestionRequest;
import com.soc.ingestion.dto.NetFlowRequest;
import com.soc.ingestion.model.EDRTelemetry;
import com.soc.ingestion.model.NetFlowRecord;
import com.soc.ingestion.model.SecurityLog;
import com.soc.ingestion.service.MultiModalIngestionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Multi-Modal Data Ingestion Controller
 * Provides endpoints for ingesting different types of security data
 */
@RestController
@RequestMapping("/api/ingestion")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class MultiModalIngestionController {
    
    private final MultiModalIngestionService ingestionService;
    
    /**
     * Ingest security log (backward compatible)
     */
    @PostMapping("/log")
    public ResponseEntity<SecurityLog> ingestLog(@Valid @RequestBody LogIngestionRequest request) {
        SecurityLog savedLog = ingestionService.ingestLog(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedLog);
    }
    
    /**
     * Ingest NetFlow record
     */
    @PostMapping("/netflow")
    public ResponseEntity<NetFlowRecord> ingestNetFlow(@Valid @RequestBody NetFlowRequest request) {
        NetFlowRecord savedRecord = ingestionService.ingestNetFlow(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedRecord);
    }
    
    /**
     * Ingest EDR telemetry
     */
    @PostMapping("/edr")
    public ResponseEntity<EDRTelemetry> ingestEDRTelemetry(@Valid @RequestBody EDRTelemetryRequest request) {
        EDRTelemetry savedTelemetry = ingestionService.ingestEDRTelemetry(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedTelemetry);
    }
    
    /**
     * Get ingestion statistics across all data types
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Long>> getStats() {
        Map<String, Long> stats = ingestionService.getIngestionStats();
        return ResponseEntity.ok(stats);
    }
}

