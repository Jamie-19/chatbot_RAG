# Makefile for RAG Chatbot Production Management

.PHONY: help install setup test clean logs health chat ingest

# Default target
help:
	@echo "RAG Chatbot Production Management"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install Python dependencies"
	@echo "  setup       - Complete setup (install + configure + ingest)"
	@echo "  test        - Run all tests"
	@echo "  clean       - Clean temporary files and logs"
	@echo "  logs        - View application logs"
	@echo "  health      - Check application health"
	@echo "  chat        - Start interactive chat"
	@echo "  ingest      - Process documents and create vector store"

# Installation
install:
	pip install -r requirements.txt

# Complete setup
setup: install
	@echo "Setting up RAG Chatbot..."
	@mkdir -p logs knowledge_base faiss_index
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env file - please edit with your configuration"; fi
	@echo "Setup complete! Run 'make ingest' to process documents."

# Testing
test:
	pytest tests/ -v --cov=. --cov-report=html

# Cleanup
clean:
	@echo "Cleaning temporary files..."
	@rm -rf __pycache__/
	@rm -rf .pytest_cache/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@echo "Cleanup complete!"

# Application commands
logs:
	@echo "Viewing application logs..."
	@tail -f logs/rag_chatbot.log 2>/dev/null || echo "No logs found"

health:
	python main.py health

chat:
	python main.py chat

ingest:
	python main.py ingest

# Development commands
dev-setup: setup
	@echo "Development setup complete!"
	@echo "Run 'make chat' to start the chatbot"

dev-test: test
	@echo "Running development tests..."

# Production commands
prod-deploy: setup
	@echo "Production deployment complete!"
	@echo "Run 'make health' to check status"

prod-logs:
	@echo "Viewing production logs..."
	@tail -n 100 logs/rag_chatbot.log 2>/dev/null || echo "No logs found"

# Monitoring
monitor:
	@echo "Application Health Status:"
	@python main.py health
	@echo ""
	@echo "Recent Logs:"
	@tail -n 20 logs/rag_chatbot.log 2>/dev/null || echo "No logs found"

# Backup
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@tar -czf backups/rag_chatbot_$(shell date +%Y%m%d_%H%M%S).tar.gz knowledge_base/ faiss_index/ logs/ .env
	@echo "Backup created in backups/ directory"
