package com.soc.ingestion.repository;

import com.soc.ingestion.model.SecurityLog;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface LogRepository extends MongoRepository<SecurityLog, String> {
    List<SecurityLog> findBySource(String source);
    
    List<SecurityLog> findByLogLevel(String logLevel);
    
    @Query("{ 'timestamp': { $gte: ?0, $lte: ?1 } }")
    List<SecurityLog> findByTimestampBetween(LocalDateTime start, LocalDateTime end);
    
    @Query("{ 'processed': false }")
    List<SecurityLog> findUnprocessedLogs();
    
    long countBySource(String source);
}

