# Production-Ready RAG Chatbot

A robust, production-ready Retrieval-Augmented Generation (RAG) chatbot built with Python, designed for enterprise deployment with comprehensive monitoring, security, and reliability features.

## 🚀 Features

### Core Functionality
- **Document Processing**: Supports PDF and TXT files
- **Vector Search**: FAISS-based similarity search
- **Local LLM**: Ollama integration with Mistral model
- **CPU-Only**: No GPU dependencies required

### Production Features
- **Security**: Input validation, sanitization, and secure deserialization
- **Monitoring**: Comprehensive metrics, health checks, and alerting
- **Logging**: Structured logging with rotation and levels
- **Error Handling**: Retry logic with exponential backoff
- **Configuration**: Environment-based settings with validation
- **Testing**: Unit tests and integration tests
- **Performance**: Caching and optimization features

## 📋 Prerequisites

- Python 3.11+
- Ollama (for local LLM)
- 4GB+ RAM recommended

## 🛠️ Installation

### Option 1: Direct Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot_RAG
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for installation)
   ollama pull mistral
   ```

5. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Run setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```


## 🚀 Usage

### Command Line Interface

```bash
# Start interactive chat
python main.py chat

# Process documents and create vector store
python main.py ingest

# Check system health
python main.py health

# Enable debug mode
python main.py chat --debug

# Specify custom log file
python main.py chat --log-file /path/to/logs/app.log
```


## 📁 Project Structure

```
chatbot_RAG/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── utils/
│   ├── __init__.py
│   ├── validation.py        # Input validation
│   ├── logging_config.py    # Logging setup
│   ├── retry.py            # Retry logic
│   └── monitoring.py       # Metrics & monitoring
├── tests/
│   ├── __init__.py
│   ├── test_validation.py  # Validation tests
│   ├── test_monitoring.py  # Monitoring tests
│   └── conftest.py         # Test fixtures
├── scripts/
│   ├── setup.sh           # Automated setup
│   └── health_check.py    # Health monitoring
├── knowledge_base/         # Document storage
├── faiss_index/           # Vector store
├── logs/                  # Log files
├── main.py               # Main application
├── rag_pipeline.py       # RAG implementation
├── vector_store.py       # Vector store management
├── data_loader.py        # Document loading
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## ⚙️ Configuration

All configuration is managed through environment variables. Copy `env.example` to `.env` and customize:

### Key Settings

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO

# Ollama Configuration
OLLAMA_MODEL_NAME=mistral
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=30

# Text Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=50
SEARCH_K=3

# Security
MAX_QUERY_LENGTH=2000
MIN_QUERY_LENGTH=2

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
```

## 📊 Monitoring

### Health Checks

```bash
# Check application health
python main.py health

# Programmatic health check
python scripts/health_check.py

# With webhook alerting
python scripts/health_check.py https://hooks.slack.com/your-webhook
```

### Metrics

The application tracks:
- Request counts and success rates
- Response times
- System resource usage (CPU, memory, disk)
- Error counts by type
- Cache hit/miss rates

### Logging

Logs are written to:
- Console (INFO level)
- File: `logs/rag_chatbot.log` (DEBUG level)
- Rotating files (10MB max, 5 backups)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_validation.py

# Run with verbose output
pytest -v
```

## 🔒 Security Features

- **Input Validation**: Comprehensive query sanitization
- **Path Security**: Protection against directory traversal
- **Safe Deserialization**: Secure FAISS index loading
- **Error Handling**: No sensitive information in error messages

## 🚀 Production Deployment

### Environment Setup

1. **Production Environment Variables**
   ```bash
   DEBUG=false
   LOG_LEVEL=WARNING
   ENABLE_METRICS=true
   ```

2. **Resource Monitoring**
   ```bash
   # Monitor system resources
   python main.py health
   ```

3. **Health Monitoring**
   ```bash
   # Add to crontab for regular health checks
   */5 * * * * /path/to/scripts/health_check.py
   ```

### Scaling Considerations

- **Horizontal Scaling**: Use load balancer with multiple instances
- **Database**: Consider external vector database for large datasets
- **Caching**: Implement Redis for response caching
- **Monitoring**: Integrate with Prometheus/Grafana

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Pull the model
   ollama pull mistral
   ```

2. **Vector Store Not Found**
   ```bash
   # Run ingestion first
   python main.py ingest
   ```

3. **Permission Denied**
   ```bash
   # Fix log directory permissions
   chmod 755 logs
   ```

4. **Memory Issues**
   ```bash
   # Reduce chunk size in .env
   CHUNK_SIZE=250
   ```

### Debug Mode

```bash
# Enable debug logging
python main.py chat --debug

# Check logs
tail -f logs/rag_chatbot.log
```

## 📈 Performance Optimization

### Recommended Settings

- **Small datasets (< 1000 docs)**: Default settings
- **Medium datasets (1000-10000 docs)**: Increase chunk size to 750
- **Large datasets (> 10000 docs)**: Use external vector database

### Monitoring Performance

```bash
# Check system metrics
python main.py health

# Monitor logs
tail -f logs/rag_chatbot.log | grep "response_time"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check this README
- **Health Check**: Run `python main.py health`

---