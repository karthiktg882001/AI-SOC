package com.soc.ingestion;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

@SpringBootApplication
@EnableKafka
public class LogIngestionServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(LogIngestionServiceApplication.class, args);
    }
}

