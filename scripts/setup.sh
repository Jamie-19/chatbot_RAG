#!/bin/bash

# Production setup script for RAG Chatbot
set -e

echo "🚀 Setting up RAG Chatbot for production..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p knowledge_base
mkdir -p faiss_index

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 logs
chmod 755 knowledge_base
chmod 755 faiss_index

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Pull Ollama model
echo "🤖 Pulling Ollama model..."
ollama pull mistral

# Run initial ingestion
echo "📚 Running initial document ingestion..."
python main.py ingest

echo "✅ Setup complete!"
echo ""
echo "To start the chatbot:"
echo "  python main.py chat"
echo ""
echo "To check health:"
echo "  python main.py health"
echo ""
echo "To run with Docker:"
echo "  docker-compose up -d"
