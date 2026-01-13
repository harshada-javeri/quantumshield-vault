#!/bin/bash
# Quick start script for QuantumShield Vault

set -e

echo "🚀 QuantumShield Vault - Quantum-Safe Crypto Wallet"
echo "=================================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker & Docker Compose found"
echo ""

# Start containers
echo "📦 Starting QuantumShield Vault stack..."
docker-compose up --build -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo ""
echo "🔍 Checking service health..."

# Backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend API healthy (http://localhost:8000)"
else
    echo "⚠️  Backend not ready yet. Try again in a moment."
fi

# Frontend health
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend running (http://localhost:3000)"
else
    echo "⚠️  Frontend not ready yet. Try again in a moment."
fi

echo ""
echo "=================================================="
echo "✨ QuantumShield Vault is ready!"
echo ""
echo "📊 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Database: localhost:5432 (postgres/quantum_secure_2027)"
echo ""
echo "🧪 Run tests:"
echo "   Backend:   docker-compose exec backend pytest -v"
echo "   Frontend:  docker-compose exec frontend npm run test"
echo ""
echo "🛑 Stop all services:"
echo "   docker-compose down"
echo ""
echo "=================================================="
