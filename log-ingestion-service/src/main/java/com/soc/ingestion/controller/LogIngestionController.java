package com.soc.ingestion.controller;

import com.soc.ingestion.dto.LogIngestionRequest;
import com.soc.ingestion.model.SecurityLog;
import com.soc.ingestion.service.LogIngestionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/logs")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class LogIngestionController {
    
    private final LogIngestionService logIngestionService;
    private final com.soc.ingestion.repository.LogRepository logRepository;
    
    @PostMapping("/ingest")
    public ResponseEntity<SecurityLog> ingestLog(@Valid @RequestBody LogIngestionRequest request) {
        SecurityLog savedLog = logIngestionService.ingestLog(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedLog);
    }
    
    @GetMapping
    public ResponseEntity<List<SecurityLog>> getLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        Pageable pageable = PageRequest.of(page, size);
        List<SecurityLog> logs = logRepository.findAll(pageable).getContent();
        return ResponseEntity.ok(logs);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalLogs", logIngestionService.getIngestionStats());
        stats.put("timestamp", java.time.LocalDateTime.now());
        return ResponseEntity.ok(stats);
    }
    
    @GetMapping("/source/{source}")
    public ResponseEntity<List<SecurityLog>> getLogsBySource(@PathVariable String source) {
        List<SecurityLog> logs = logRepository.findBySource(source);
        return ResponseEntity.ok(logs);
    }
}

