# QuantumShield Vault - Deployment & Quick Start Guide

## 🚀 5-Minute Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start
git clone https://github.com/yourusername/quantumshield-vault
cd quantumshield-vault
chmod +x start.sh
./start.sh

# Or with Docker Compose directly
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
```

### Option 2: Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
# Backend ready at http://localhost:8000
```

#### Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
# Frontend ready at http://localhost:3000
```

---

## 📊 Project Statistics

```
Backend Code:
  ✓ main.py (400 lines) - FastAPI routes
  ✓ models.py (100 lines) - Database models
  ✓ crud.py (250 lines) - Database operations
  ✓ schemas.py (250 lines) - Pydantic validation
  ✓ crypto/ecdsa_wallet.py (150 lines) - ECDSA implementation
  ✓ crypto/dilithium_wallet.py (150 lines) - Post-quantum crypto
  ✓ mcp_tools.py (200 lines) - MCP integration
  ✓ tests/test_backend.py (600 lines) - 90%+ coverage

Frontend Code:
  ✓ src/App.tsx (80 lines) - Root component
  ✓ src/components/WalletDashboard.tsx (200 lines) - Dashboard UI
  ✓ src/components/AttackSimulator.tsx (180 lines) - Attack demo
  ✓ src/components/MigrationAgent.tsx (200 lines) - Migration UI
  ✓ src/lib/api.ts (120 lines) - API client
  ✓ src/lib/hooks.ts (100 lines) - React hooks
  ✓ tests/* (150 lines) - Unit tests

Infrastructure:
  ✓ docker-compose.yml - Full stack setup
  ✓ .github/workflows/ci-cd.yml - GitHub Actions pipeline
  ✓ openapi.yaml - Complete API specification
  ✓ Makefile - Development commands
  ✓ render.yaml - Render deployment blueprint

Total: ~3,500+ lines of production-ready code
```

---

## 🔧 Available Make Commands

```bash
make install       # Install all dependencies
make dev          # Start development environment
make test         # Run all tests with coverage
make test-backend # Backend tests only
make test-frontend# Frontend tests only
make lint         # Check code quality
make format       # Format code automatically
make build        # Build Docker images
make up           # Start Docker stack
make down         # Stop Docker stack
make clean        # Remove build artifacts
make db-reset     # Reset database to fresh state
make logs         # Show live logs
make help         # Show all available commands
```

---

## 🌐 Deploying to Render.com

### Prerequisites
- Render.com account (free tier available)
- GitHub repository with this code
- PostgreSQL database (optional - Render can create)

### Step-by-Step

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: QuantumShield Vault"
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create Backend Service**
   - New → Web Service
   - Connect GitHub repo
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `cd backend && python main.py`
   - Environment: Python
   - Add environment variables:
     - `DATABASE_ENV=production`
     - `DATABASE_URL=postgresql://...` (from PostgreSQL service)
   - Deploy

4. **Create PostgreSQL Database**
   - New → PostgreSQL
   - Choose instance (free tier available)
   - Copy connection string

5. **Create Frontend Service**
   - New → Static Site
   - Connect GitHub repo
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
   - Deploy

6. **Update Environment Variables**
   - Frontend: `VITE_API_URL=https://your-backend.onrender.com`
   - Backend: `DATABASE_URL=your-postgres-url`

### Expected URLs After Deployment
- Frontend: `https://quantumshield-vault-xxxxx.onrender.com`
- API: `https://quantumshield-api-xxxxx.onrender.com`
- API Docs: `https://quantumshield-api-xxxxx.onrender.com/docs`

**Cost:** $0/month with Render's free tier (requires account verification)

---

## 🧪 Testing Guide

### Backend Tests
```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=. --cov-report=html
# View report: open htmlcov/index.html

# Run specific test
pytest tests/test_backend.py::TestECDSACrypto::test_sign_and_verify -v

# Run with output capture
pytest -v -s
```

### Frontend Tests
```bash
cd frontend

# Unit tests
npm run test

# With coverage
npm run coverage

# E2E tests (requires running app)
npm run e2e
```

### Test Coverage
- **Backend:** 90%+ (ECDSA, Dilithium, CRUD, migrations)
- **Frontend:** Unit tests for utilities and hooks
- **Integration:** Docker Compose tests

---

## 🔐 Security Checklist

### Before Production
- [ ] Change all default passwords in `.env.production`
- [ ] Enable HTTPS/TLS (Render does this automatically)
- [ ] Set up API rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Review and update security headers
- [ ] Run security audit: `trivy scan .`
- [ ] Review database backups
- [ ] Set up monitoring/alerting

### Cryptographic Security
- [ ] ECDSA keys stored securely (encrypted at rest)
- [ ] Dilithium keys never transmitted insecurely
- [ ] All API calls use HTTPS in production
- [ ] Database uses SSL connections
- [ ] Audit logs enabled for all migrations

---

## 📈 Monitoring & Logs

### Docker Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Follow with timestamps
docker-compose logs -f --timestamps
```

### API Health
```bash
# Production health check
curl https://your-api.onrender.com/health

# Database health
curl https://your-api.onrender.com/health | jq '.database'

# MCP server status
curl https://your-api.onrender.com/health | jq '.mcp_server'
```

### Database Queries
```bash
# Connect to PostgreSQL
psql -U quantumshield -d quantumshield -h localhost

# Check migrations
SELECT * FROM migration_logs ORDER BY created_at DESC LIMIT 10;

# Check wallet status
SELECT id, name, is_migrated, balance_qsv FROM wallets;

# Attack stats
SELECT COUNT(*) as total, SUM(CASE WHEN signature_broken THEN 1 ELSE 0 END) as broken FROM attack_logs;
```

---

## 🆘 Troubleshooting

### Docker Issues
```bash
# Containers won't start
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v  # Remove volumes
docker-compose up --build

# Port already in use
# Change ports in docker-compose.yml and try again
```

### Database Issues
```bash
# Reset database
docker-compose exec backend python -c "from database import init_db; init_db()"

# Connect directly
docker-compose exec db psql -U quantumshield -d quantumshield

# Migrations failed
docker-compose exec backend python -c "from models import Base; from database import engine; Base.metadata.create_all(bind=engine)"
```

### Frontend Not Loading
```bash
# Check Node modules
cd frontend && npm install

# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Check API URL
echo $VITE_API_URL
# Should be http://localhost:8000 for dev
```

### API Responses Slow
```bash
# Check database performance
# Monitor with: docker-compose logs -f backend

# Scale services
docker-compose up --scale backend=3

# Check resource usage
docker stats
```

---

## 📚 API Examples

### Create User & Wallet Workflow

```bash
# 1. Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com"
  }'
# Response: {"id": 1, "username": "alice", ...}

# 2. Create wallet (save user_id from above)
curl -X POST http://localhost:8000/wallet \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "My First Wallet"
  }'
# Response: {"id": 1, "ecdsa_address": "0x...", "balance_qsv": 1.0, ...}

# 3. Get dashboard
curl http://localhost:8000/user/1/dashboard
# Response: Complete user overview with all wallets

# 4. Simulate attack
curl -X POST http://localhost:8000/simulate-attack/1
# Response: {"attack_successful": true, "quantum_vulnerable": true, ...}

# 5. Migrate to Dilithium
curl -X POST http://localhost:8000/migrate/1
# Response: {"success": true, "new_keys": {...}, "migration_id": 42}

# 6. Verify migration
curl http://localhost:8000/wallet/1/crypto-audit
# Response: {"current_algorithm": "Dilithium", "quantum_threat_status": "NONE", ...}
```

### Batch Operations

```bash
# Get all migrations for user
curl http://localhost:8000/user/1/migrations

# Get network statistics
curl http://localhost:8000/stats/migration
curl http://localhost:8000/stats/attacks

# Get all user wallets
curl http://localhost:8000/user/1/wallets
```

---

## 🚀 Performance Tips

### Backend Optimization
```python
# Use connection pooling (already configured)
# Pool size: 10, max overflow: 20

# Database indexes on frequently queried columns:
# - users.username
# - users.email
# - wallets.user_id
# - wallets.is_migrated
# - migration_logs.user_id

# Cache frequently accessed data
# Use Redis for session management (optional)
```

### Frontend Optimization
```typescript
// Code splitting with React.lazy()
const WalletDashboard = React.lazy(() => import('./components/WalletDashboard'));

// Memoization to prevent unnecessary re-renders
const MemoizedWallet = React.memo(WalletCard);

// API call caching with React Query patterns
```

---

## 📦 Dependency Management

### Update Dependencies
```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
npm audit fix
```

### Remove Unused Dependencies
```bash
# Backend
pip list --outdated
pip uninstall unused_package

# Frontend
npm prune
npx npm-check-updates -u
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Push to Main:**
   - ✓ Runs backend tests
   - ✓ Runs frontend tests
   - ✓ Builds Docker images
   - ✓ Pushes to GitHub Container Registry
   - ✓ Triggers Render deployment

2. **Pull Requests:**
   - ✓ Runs all tests
   - ✓ Code quality checks
   - ✓ Security scans

View workflow status: `.github/workflows/ci-cd.yml`

---

## 📝 Key Files Reference

| File | Purpose |
|------|---------|
| `README.md` | Architecture & threat analysis |
| `AGENTS.md` | MCP integration documentation |
| `openapi.yaml` | REST API specification |
| `docker-compose.yml` | Local development setup |
| `Makefile` | Development commands |
| `backend/main.py` | FastAPI application |
| `backend/models.py` | Database schema |
| `frontend/src/App.tsx` | React root component |
| `.github/workflows/ci-cd.yml` | Deployment pipeline |

---

## 🎓 Learning Resources

This project demonstrates:
- ✓ **Cryptography:** ECDSA vs post-quantum (Dilithium)
- ✓ **Backend:** FastAPI + SQLAlchemy + async Python
- ✓ **Frontend:** React + TypeScript + modern tooling
- ✓ **DevOps:** Docker, CI/CD, infrastructure
- ✓ **AI Integration:** MCP tools for autonomous agents
- ✓ **Database:** SQL design, migrations, indexing
- ✓ **Testing:** Unit, integration, end-to-end
- ✓ **Security:** Input validation, CORS, auth patterns

Perfect for learning production-grade full-stack development! 🚀

---

## 💬 Support & Questions

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** support@quantumshield.local

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

**Happy deploying! 🛡️⚡**
