# CORE AI Chatbot - Quick Reference Guide

> **Fast reference for common tasks and operations**

---

## 📋 Quick Navigation

- [Setup Commands](#setup-commands)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Operations](#database-operations)
- [Testing](#testing)
- [Docker Commands](#docker-commands)
- [Debugging](#debugging)
- [Environment Variables](#environment-variables)

---

## 🚀 Setup Commands

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd core-ai-chatbot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-enterprise.txt
cp .env.example .env
# Edit .env with your settings

# Frontend setup
cd ../frontend
npm install
```

### Database Initialization

```bash
# Quick init (creates tables)
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Using Alembic (recommended for production)
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## ▶️ Running the Application

### Development Mode

```bash
# Backend (with auto-reload)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev

# Both with one command
# Terminal 1: cd backend && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

### Production Mode

```bash
# Backend (multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend (build and serve)
npm run build
npm run preview
```

### Docker

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Stop all
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/conversations` | List all conversations |
| `POST` | `/conversations` | Create new conversation |
| `GET` | `/conversations/{id}` | Get conversation details |
| `PUT` | `/conversations/{id}` | Update conversation |
| `DELETE` | `/conversations/{id}` | Delete conversation |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send message (non-streaming) |
| `POST` | `/chat/stream` | Send message (streaming SSE) |

### Health Checks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health |
| `GET` | `/health/db` | Database health |
| `GET` | `/health/ai` | AI service health |

### Examples

#### Create Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "My Chat"}'
```

#### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "conversation_id": "your-conv-id",
    "temperature": 0.7
  }'
```

#### Get Conversations
```bash
curl http://localhost:8000/api/v1/conversations
```

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

---

## 💾 Database Operations

### Alembic Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history

# Rollback to specific version
alembic downgrade <revision_id>
```

### Database Access

```bash
# PostgreSQL
psql -U chatbot_user -d chatbot_db

# MySQL
mysql -u chatbot_user -p chatbot_db

# SQLite
sqlite3 chatbot.db

# Docker PostgreSQL
docker exec -it chatbot_postgres psql -U chatbot_user -d chatbot_db
```

### Common Queries

```sql
-- List conversations
SELECT id, title, created_at FROM conversations ORDER BY updated_at DESC LIMIT 10;

-- Count messages by conversation
SELECT conversation_id, COUNT(*) FROM messages GROUP BY conversation_id;

-- Recent activity
SELECT * FROM conversations WHERE updated_at > NOW() - INTERVAL '7 days';

-- Token usage
SELECT SUM(total_tokens) FROM messages WHERE created_at > NOW() - INTERVAL '1 day';
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Specific test file
pytest tests/integration/test_api.py -v

# Specific test function
pytest tests/unit/test_services.py::test_function_name -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -v -s
```

### Coverage Report

```bash
# Generate HTML report
pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

---

## 🐳 Docker Commands

### Build & Run

```bash
# Build image
docker build -t chatbot-api:latest ./backend

# Run container
docker run -d --name chatbot-api -p 8000:8000 chatbot-api:latest

# Stop container
docker stop chatbot-api

# Remove container
docker rm chatbot-api

# View logs
docker logs -f chatbot-api
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d backend postgres redis

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f backend

# Rebuild services
docker-compose up -d --build

# Scale services
docker-compose up -d --scale backend=3

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U chatbot_user

# View running services
docker-compose ps
```

### Useful Docker Commands

```bash
# List all containers
docker ps -a

# List all images
docker images

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# View container stats
docker stats

# Inspect container
docker inspect chatbot-api
```

---

## 🐛 Debugging

### View Logs

```bash
# Application logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend

# Last 100 lines
tail -n 100 backend/logs/app.log

# Search logs
grep ERROR backend/logs/app.log

# Watch logs in real-time
watch -n 1 tail -n 20 backend/logs/app.log
```

### Python Debugger

```python
# Add to code
import ipdb; ipdb.set_trace()

# Or use breakpoint()
breakpoint()
```

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Database Connection Error
```bash
# Check database is running
docker-compose ps postgres

# Check connection
psql -U chatbot_user -h localhost -d chatbot_db

# Restart database
docker-compose restart postgres
```

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements-enterprise.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify app is importable
python -c "from app.main import app; print('OK')"
```

---

## 🔧 Environment Variables

### Required Variables

```env
MISTRAL_API_KEY=your_api_key_here
SECRET_KEY=your-secret-key-minimum-32-characters
```

### Database URLs

```env
# SQLite (Development)
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# PostgreSQL (Production)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/chatbot_db

# MySQL
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/chatbot_db

# MongoDB
DATABASE_URL=mongodb://localhost:27017/chatbot_db
```

### Environment Modes

```env
# Development
ENVIRONMENT=development
DEBUG=true

# Production
ENVIRONMENT=production
DEBUG=false
```

---

## 🛠️ Code Quality

### Format & Lint

```bash
# Format code with black
black app/

# Sort imports
isort app/

# Lint with flake8
flake8 app/

# Advanced linting
pylint app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

### Run All Checks

```bash
# One-liner for all checks
black app/ && isort app/ && flake8 app/ && mypy app/ && pytest tests/ -v
```

---

## 📊 Monitoring

### Application Metrics

```bash
# Request count
curl http://localhost:8000/metrics | grep http_requests_total

# Response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health
```

### Database Performance

```sql
-- Slow queries (PostgreSQL)
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🔑 Secrets Management

### Generate Secret Key

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### API Key Management

```python
# Generate API key
from app.core.security import generate_api_key
api_key = generate_api_key(prefix="sk")
print(api_key)
```

---

## 📝 Common Tasks

### Add New Endpoint

1. Create endpoint in `app/api/v1/endpoints/`
2. Add to router in `app/api/v1/router.py`
3. Create Pydantic schemas in `app/schemas/`
4. Write tests in `tests/integration/`

### Add New Database Model

1. Define model in `app/models/`
2. Create Pydantic schema in `app/schemas/`
3. Create repository in `app/repositories/`
4. Generate migration: `alembic revision --autogenerate`
5. Apply migration: `alembic upgrade head`

### Add New Service

1. Create service in `app/services/`
2. Inject dependencies via `__init__`
3. Write business logic methods
4. Write unit tests in `tests/unit/`

---

## 🔗 Useful URLs

### Local Development

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Adminer: http://localhost:8080
- Redis Commander: http://localhost:8081
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### Production

- Update these with your actual production URLs

---

## 📞 Support Commands

### System Info

```bash
# Python version
python --version

# Pip packages
pip list

# FastAPI version
python -c "import fastapi; print(fastapi.__version__)"

# Database version
psql --version

# Docker version
docker --version
docker-compose --version

# Node version
node --version
npm --version
```

### Health Checks

```bash
# Quick health check
curl http://localhost:8000/api/v1/health | jq

# Database connectivity
python -c "from app.core.database import check_db_health; import asyncio; print(asyncio.run(check_db_health()))"

# AI service validation
python -c "from app.services.ai_service import ai_service; import asyncio; print(asyncio.run(ai_service.validate_api_key()))"
```

---

## 📚 Additional Resources

- [Enterprise Architecture](ENTERPRISE_ARCHITECTURE.md) - Complete architecture guide
- [Migration Guide](MIGRATION_GUIDE.md) - Step-by-step migration
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - What was implemented
- [Enterprise README](ENTERPRISE_README.md) - Full documentation

---

**Last Updated:** 2024  
**Version:** 1.0.0  
**Maintained by:** Development Team