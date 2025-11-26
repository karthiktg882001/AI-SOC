package com.soc.ingestion.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class MLServiceClient {
    
    @Value("${ml.service.url:http://ml-service:8000}")
    private String mlServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    public void triggerDirectDetection(Map<String, Object> logData) {
        try {
            String url = mlServiceUrl + "/api/direct/detect";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> request = new HashMap<>();
            request.put("logData", logData);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> result = response.getBody();
                if (result != null && Boolean.TRUE.equals(result.get("threat_detected"))) {
                    log.info("Threat detected via direct detection: {} (Severity: {})", 
                        result.get("threat_type"), result.get("severity"));
                }
            }
        } catch (Exception e) {
            log.error("Error calling ML service for direct detection: {}", e.getMessage());
            // Don't fail log ingestion if ML service is unavailable
        }
    }
}

