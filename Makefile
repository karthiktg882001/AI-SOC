.PHONY: help build up down restart logs clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-ml: ## Show logs from ML service
	docker-compose logs -f ml-service

logs-ingestion: ## Show logs from log ingestion service
	docker-compose logs -f log-ingestion-service

logs-frontend: ## Show logs from frontend
	docker-compose logs -f frontend

clean: ## Stop and remove all containers, volumes, and networks
	docker-compose down -v --remove-orphans

test: ## Run API tests
	chmod +x scripts/test_api.sh
	./scripts/test_api.sh

generate-logs: ## Generate sample logs
	python3 scripts/generate_sample_logs.py

ps: ## Show running containers
	docker-compose ps

status: ## Show service status
	@echo "=== Service Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Health Checks ==="
	@echo "ML Service:" && curl -s http://localhost:8000/health | python3 -m json.tool || echo "Not available"
	@echo ""
	@echo "Log Ingestion:" && curl -s http://localhost:8080/api/logs/stats | python3 -m json.tool || echo "Not available"

