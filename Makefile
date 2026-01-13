.PHONY: help install dev test build up down clean

help:
	@echo "QuantumShield Vault - Makefile Commands"
	@echo "========================================"
	@echo ""
	@echo "Installation & Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make dev          - Start development environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo "  make coverage     - Generate coverage reports"
	@echo ""
	@echo "Docker:"
	@echo "  make up           - Start Docker Compose stack"
	@echo "  make down         - Stop Docker Compose stack"
	@echo "  make build        - Build Docker images"
	@echo ""
	@echo "Development:"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black/prettier"
	@echo "  make clean        - Remove build artifacts"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✓ Dependencies installed"

dev:
	@echo "🚀 Starting development environment..."
	@echo "Starting backend..."
	cd backend && python main.py &
	@echo "Starting frontend..."
	cd frontend && npm run dev &
	@echo "✓ Development environment running"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

test: test-backend test-frontend
	@echo "✓ All tests passed"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && pytest -v --cov=. --cov-report=html
	@echo "✓ Backend tests passed (see htmlcov/index.html)"

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm run test
	@echo "✓ Frontend tests passed"

coverage:
	@echo "📊 Generating coverage reports..."
	cd backend && pytest -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "✓ Backend coverage report: htmlcov/index.html"
	cd frontend && npm run coverage
	@echo "✓ Frontend coverage generated"

lint:
	@echo "🔍 Running linters..."
	cd backend && flake8 . --max-line-length=100 --exclude=venv,migrations
	cd backend && black --check . --exclude=venv
	cd backend && isort --check-only .
	cd frontend && npm run lint
	@echo "✓ No linting issues found"

format:
	@echo "🎨 Formatting code..."
	cd backend && black . --exclude=venv
	cd backend && isort .
	cd frontend && npx prettier --write src
	@echo "✓ Code formatted"

build:
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "✓ Docker images built"

up:
	@echo "🚀 Starting Docker stack..."
	docker-compose up -d
	@echo "⏳ Waiting for services..."
	sleep 10
	@echo "✓ Stack is running"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

down:
	@echo "🛑 Stopping Docker stack..."
	docker-compose down
	@echo "✓ Stack stopped"

logs:
	@echo "📜 Showing logs (Ctrl+C to exit)..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up..."
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

db-reset:
	@echo "🔄 Resetting database..."
	rm -f data/quantumshield.db
	cd backend && python -c "from database import init_db; init_db()"
	@echo "✓ Database reset"

migrate-up:
	@echo "📤 Running database migrations..."
	cd backend && alembic upgrade head

migrate-down:
	@echo "📥 Reverting database migrations..."
	cd backend && alembic downgrade base

# Utility commands
shell-backend:
	cd backend && python

shell-psql:
	psql -U quantumshield -d quantumshield -h localhost

docker-shell-backend:
	docker-compose exec backend /bin/bash

docker-shell-frontend:
	docker-compose exec frontend /bin/sh

stats:
	@echo "📊 Repository Statistics"
	@echo "========================"
	@wc -l backend/**/*.py frontend/src/**/*.tsx
	@echo ""
	@echo "Git commits: $$(git rev-list --count HEAD)"
