package com.soc.ingestion.repository;

import com.soc.ingestion.model.NetFlowRecord;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface NetFlowRepository extends MongoRepository<NetFlowRecord, String> {
    List<NetFlowRecord> findBySourceIp(String sourceIp);
    List<NetFlowRecord> findByDestinationIp(String destinationIp);
    List<NetFlowRecord> findByTimestampBetween(LocalDateTime start, LocalDateTime end);
    List<NetFlowRecord> findByProtocol(String protocol);
}

