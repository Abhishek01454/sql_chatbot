# Enterprise Architecture Documentation

## Overview

This document outlines the enterprise-grade architecture implemented for the CORE AI Chatbot application. The architecture follows industry best practices, design patterns, and principles to ensure scalability, maintainability, security, and reliability.

## Architecture Principles

### 1. **Separation of Concerns**
- Clear separation between presentation, business logic, and data layers
- Each component has a single, well-defined responsibility
- Easy to understand, test, and modify individual components

### 2. **Dependency Injection**
- Loose coupling between components
- Dependencies are injected rather than hard-coded
- Facilitates testing with mock objects

### 3. **Repository Pattern**
- Abstraction layer between business logic and data access
- Easy to swap databases or add caching
- Testable without actual database

### 4. **Service Layer**
- Business logic encapsulated in service classes
- Reusable across different endpoints
- Single source of truth for business operations

### 5. **API Versioning**
- Versioned API endpoints (v1, v2, etc.)
- Backward compatibility support
- Smooth migration path for clients

### 6. **Configuration Management**
- Centralized configuration using environment variables
- Environment-specific settings (dev, staging, production)
- Type-safe configuration with Pydantic

### 7. **Logging and Monitoring**
- Structured logging with JSON format
- Request tracing and correlation IDs
- Performance metrics and health checks

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # API v1 router
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── conversations.py  # Conversation endpoints
│   │   │       ├── chat.py          # Chat endpoints
│   │   │       ├── health.py        # Health check endpoints
│   │   │       └── auth.py          # Authentication endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # Database setup and session
│   │   ├── security.py              # Security utilities (JWT, hashing)
│   │   └── logging_config.py        # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── conversation.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── conversation.py          # Pydantic schemas
│   │   ├── auth.py                  # Auth schemas
│   │   └── common.py                # Common schemas
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base repository with CRUD
│   │   ├── conversation_repository.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py            # AI/LLM integration
│   │   ├── conversation_service.py  # Conversation business logic
│   │   └── auth_service.py          # Authentication logic
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py         # Global error handling
│   │   ├── rate_limiter.py          # Rate limiting
│   │   ├── request_logger.py        # Request/response logging
│   │   └── cors.py                  # CORS configuration
│   └── utils/
│       ├── __init__.py
│       ├── validators.py            # Custom validators
│       ├── helpers.py               # Helper functions
│       └── exceptions.py            # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration
│   ├── unit/
│   │   ├── test_services.py
│   │   ├── test_repositories.py
│   │   └── test_utils.py
│   └── integration/
│       ├── test_api.py
│       └── test_database.py
├── logs/                            # Application logs
├── .env                             # Environment variables
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
├── alembic/                         # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Layer Descriptions

### 1. API Layer (Presentation Layer)

**Purpose**: Handle HTTP requests and responses

**Components**:
- **Endpoints**: FastAPI route handlers
- **Request Validation**: Pydantic models for input validation
- **Response Formatting**: Standardized response structures
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

**Best Practices**:
- Thin controllers - minimal logic
- Delegate to service layer
- Consistent response formats
- Proper HTTP status codes
- Comprehensive error handling

### 2. Service Layer (Business Logic Layer)

**Purpose**: Implement business rules and orchestrate operations

**Components**:
- **AIService**: Handles AI model interactions
- **ConversationService**: Manages conversation logic
- **AuthService**: Handles authentication and authorization

**Responsibilities**:
- Business logic implementation
- Transaction management
- Cross-cutting concerns
- Data transformation
- Error handling and validation

**Best Practices**:
- Single Responsibility Principle
- Dependency injection
- Testable without database
- Clear method signatures
- Comprehensive error handling

### 3. Repository Layer (Data Access Layer)

**Purpose**: Abstract database operations

**Components**:
- **BaseRepository**: Generic CRUD operations
- **ConversationRepository**: Conversation-specific queries
- **MessageRepository**: Message-specific queries

**Responsibilities**:
- Database queries
- Data persistence
- Query optimization
- Transaction management

**Best Practices**:
- Repository pattern
- Async database operations
- Query optimization
- Proper indexing
- Connection pooling

### 4. Models Layer (Domain Layer)

**Purpose**: Define data structures and relationships

**Components**:
- **SQLAlchemy Models**: Database schema definitions
- **Pydantic Schemas**: API request/response models

**Types**:
- **ORM Models** (`models/`): Database representation
- **Request Schemas** (`schemas/`): API input validation
- **Response Schemas** (`schemas/`): API output formatting

### 5. Core Layer (Infrastructure Layer)

**Purpose**: Provide foundational services

**Components**:
- **Configuration**: Environment-based settings
- **Database**: Connection and session management
- **Security**: Authentication, encryption, JWT
- **Logging**: Structured logging configuration

## Key Components

### Configuration Management

```python
# app/core/config.py
class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "CORE AI Chatbot API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # AI Service
    MISTRAL_API_KEY: str
    MISTRAL_MODEL: str = "mistral-small-latest"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
```

**Features**:
- Type-safe configuration
- Environment variable loading
- Validation on startup
- Multiple environment support
- Sensible defaults

### Database Management

**Support for**:
- PostgreSQL (production recommended)
- MySQL/MariaDB
- SQLite (development/testing)
- MongoDB (alternative document store)

**Features**:
- Async database operations
- Connection pooling
- Migration support (Alembic)
- Health checks
- Automatic session management

### Security Implementation

**Authentication**:
- JWT tokens (access + refresh)
- Password hashing (bcrypt)
- API key support
- OAuth2 compatible

**Authorization**:
- Role-based access control (RBAC)
- Resource-level permissions
- User context propagation

**Security Features**:
- CORS configuration
- Rate limiting
- Input sanitization
- SQL injection prevention
- XSS protection

### Logging System

**Features**:
- Structured JSON logging
- Multiple log levels
- File rotation
- Request tracing
- Performance metrics

**Log Formats**:
- **Development**: Colored console output
- **Production**: JSON format for log aggregation

**Logged Information**:
- Request/response details
- Processing time
- Error stack traces
- User actions
- System events

### Error Handling

**Strategy**:
- Global exception handlers
- Custom exception classes
- Standardized error responses
- Detailed error logging

**Error Response Format**:
```json
{
  "error": "ValidationError",
  "message": "Invalid input format",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  },
  "request_id": "req_abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Design

### Versioning Strategy

- URL versioning: `/api/v1/`, `/api/v2/`
- Backward compatibility maintained
- Deprecation notices in responses
- Migration guides provided

### Endpoint Structure

```
GET    /api/v1/conversations           # List all conversations
POST   /api/v1/conversations           # Create new conversation
GET    /api/v1/conversations/{id}      # Get conversation details
PUT    /api/v1/conversations/{id}      # Update conversation
DELETE /api/v1/conversations/{id}      # Delete conversation

POST   /api/v1/chat                    # Send chat message
POST   /api/v1/chat/stream             # Send message (streaming)

GET    /api/v1/health                  # Health check
GET    /api/v1/health/db               # Database health
GET    /api/v1/health/ai               # AI service health

POST   /api/v1/auth/login              # User login
POST   /api/v1/auth/refresh            # Refresh token
POST   /api/v1/auth/logout             # User logout
```

### Response Standards

**Success Response**:
```json
{
  "success": true,
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {}
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## Data Flow

### Chat Request Flow

1. **Client** → Sends POST request to `/api/v1/chat`
2. **Middleware** → Validates, authenticates, logs request
3. **Endpoint** → Parses request, validates input
4. **Service Layer** → Processes business logic
5. **Repository** → Retrieves conversation history
6. **AI Service** → Calls Mistral API
7. **Repository** → Saves message to database
8. **Service Layer** → Formats response
9. **Endpoint** → Returns response to client
10. **Middleware** → Logs response, updates metrics

### Streaming Chat Flow

1. Client establishes SSE connection
2. Backend opens streaming connection to AI API
3. Chunks received from AI are immediately forwarded
4. Full response assembled in background
5. Message saved to database when complete
6. Stream closed with completion signal

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    system_prompt TEXT,
    user_id VARCHAR(36),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    temperature VARCHAR(10),
    max_tokens INTEGER,
    model_name VARCHAR(100),
    metadata JSON,
    
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_updated (updated_at),
    INDEX idx_deleted (is_deleted, updated_at)
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    model_name VARCHAR(100),
    finish_reason VARCHAR(50),
    processing_time_ms INTEGER,
    metadata JSON,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_created (conversation_id, created_at),
    INDEX idx_role (role)
);
```

### Users Table

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    api_key_hash VARCHAR(255) UNIQUE,
    metadata JSON,
    
    INDEX idx_email_active (email, is_active)
);
```

## Testing Strategy

### Unit Tests

**Scope**: Individual functions and classes

**Tools**: pytest, pytest-asyncio, pytest-mock

**Coverage**:
- Service layer methods
- Repository methods
- Utility functions
- Validators

**Example**:
```python
async def test_conversation_service_create():
    # Arrange
    mock_repo = Mock()
    service = ConversationService(mock_repo)
    
    # Act
    result = await service.create_conversation("Test Chat")
    
    # Assert
    assert result.title == "Test Chat"
    mock_repo.create.assert_called_once()
```

### Integration Tests

**Scope**: Multiple components working together

**Tools**: pytest, httpx, TestClient

**Coverage**:
- API endpoints
- Database operations
- Authentication flow
- Error handling

**Example**:
```python
async def test_chat_endpoint(client, db):
    # Create conversation
    response = await client.post("/api/v1/conversations")
    conv_id = response.json()["data"]["id"]
    
    # Send message
    response = await client.post(
        "/api/v1/chat",
        json={"message": "Hello", "conversation_id": conv_id}
    )
    
    assert response.status_code == 200
    assert "message" in response.json()["data"]
```

### End-to-End Tests

**Scope**: Complete user workflows

**Tools**: Playwright, Selenium

**Coverage**:
- User registration/login
- Creating conversations
- Sending messages
- Managing sessions

## Deployment Architecture

### Development Environment

```
┌─────────────┐
│   Frontend  │ (localhost:3000)
│   (Vite)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │ (localhost:8000)
│  (FastAPI)  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   SQLite    │ (local file)
└─────────────┘
```

### Production Environment

```
┌─────────────┐
│     CDN     │ (Static Assets)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Load Balancer│
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       ↓                ↓                ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Backend 1  │  │  Backend 2  │  │  Backend N  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │    Redis    │  │ Mistral API │
│  (Primary)  │  │   (Cache)   │  │  (External) │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Docker Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/chatbot
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=chatbot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Performance Optimization

### Backend Optimizations

1. **Database**:
   - Proper indexing on frequently queried fields
   - Connection pooling
   - Query optimization with EXPLAIN
   - Eager loading for relationships
   - Caching frequent queries

2. **API**:
   - Response compression (gzip)
   - Pagination for large datasets
   - Efficient serialization
   - Async operations
   - Rate limiting

3. **Caching**:
   - Redis for session storage
   - Cache frequently accessed data
   - Cache invalidation strategies
   - CDN for static assets

### Frontend Optimizations

1. **Code Splitting**: Load only necessary code
2. **Lazy Loading**: Load components on demand
3. **Memoization**: Cache component renders
4. **Debouncing**: Reduce API calls
5. **Virtual Scrolling**: Handle large lists
6. **Asset Optimization**: Compress images/fonts

## Monitoring and Observability

### Health Checks

- Application health endpoint
- Database connectivity check
- AI service availability
- Memory and CPU usage
- Disk space monitoring

### Metrics

- Request rate (requests/sec)
- Response time (avg, p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- AI API latency
- Token usage

### Logging

- Application logs
- Access logs
- Error logs
- Audit logs
- Performance logs

### Alerting

- Service downtime
- High error rates
- Slow response times
- Database issues
- Resource exhaustion

## Security Best Practices

### Application Security

1. **Input Validation**: Validate all user inputs
2. **Output Encoding**: Prevent XSS attacks
3. **Parameterized Queries**: Prevent SQL injection
4. **Authentication**: Secure user authentication
5. **Authorization**: Proper access control
6. **HTTPS Only**: Encrypt all traffic
7. **CORS**: Restrict cross-origin requests
8. **Rate Limiting**: Prevent abuse

### Data Security

1. **Encryption at Rest**: Encrypt sensitive data
2. **Encryption in Transit**: Use TLS/SSL
3. **Password Hashing**: bcrypt with salt
4. **API Key Security**: Hash and rotate keys
5. **Secrets Management**: Use environment variables
6. **Backup Strategy**: Regular encrypted backups

### Infrastructure Security

1. **Firewall Rules**: Restrict network access
2. **Security Updates**: Keep dependencies updated
3. **Dependency Scanning**: Check for vulnerabilities
4. **Container Security**: Scan Docker images
5. **Access Control**: Principle of least privilege

## Scalability Considerations

### Horizontal Scaling

- Stateless application design
- Load balancing across instances
- Session storage in Redis
- Database read replicas
- CDN for static content

### Vertical Scaling

- Optimize resource usage
- Increase server capacity
- Database tuning
- Caching strategies

### Database Scaling

- Read replicas for read-heavy workloads
- Sharding for large datasets
- Connection pooling
- Query optimization
- Archiving old data

## Migration Guide

### From Monolith to Enterprise

1. **Phase 1**: Restructure code (this document)
2. **Phase 2**: Add database support
3. **Phase 3**: Implement authentication
4. **Phase 4**: Add caching layer
5. **Phase 5**: Containerization
6. **Phase 6**: CI/CD pipeline
7. **Phase 7**: Monitoring setup
8. **Phase 8**: Production deployment

### Running Both Versions

The old `main.py` and new structure can coexist:
- Keep old `main.py` as `main_legacy.py`
- New entry point: `app/main.py`
- Gradual migration of endpoints
- Feature flags for toggling

## Development Workflow

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

### Code Quality

```bash
# Linting
flake8 app/
pylint app/

# Type checking
mypy app/

# Formatting
black app/
isort app/

# Security scanning
bandit -r app/
safety check
```

## Conclusion

This enterprise architecture provides:

- ✅ **Scalability**: Handle growing traffic and data
- ✅ **Maintainability**: Easy to understand and modify
- ✅ **Testability**: Comprehensive test coverage
- ✅ **Security**: Industry-standard security practices
- ✅ **Performance**: Optimized for speed and efficiency
- ✅ **Reliability**: Robust error handling and recovery
- ✅ **Observability**: Comprehensive logging and monitoring
- ✅ **Flexibility**: Easy to extend and customize

The architecture follows SOLID principles, clean architecture patterns, and industry best practices, making it suitable for production use in enterprise environments.