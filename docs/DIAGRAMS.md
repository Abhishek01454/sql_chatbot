# CORE AI Chatbot - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  React Frontend │  │   Mobile App    │  │  External APIs  │            │
│  │   (Port 3000)   │  │    (Future)     │  │   (3rd Party)   │            │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            └─────────────────────┴─────────────────────┘
                                  │
                         HTTP/HTTPS (REST API)
                                  │
┌─────────────────────────────────┼─────────────────────────────────────────────┐
│                                 ▼                                              │
│                        REVERSE PROXY / LOAD BALANCER                          │
│                        (Nginx / ALB / Cloud LB)                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│   Backend API     │  │   Backend API     │  │   Backend API     │
│   Instance 1      │  │   Instance 2      │  │   Instance N      │
│  (Port 8000)      │  │  (Port 8000)      │  │  (Port 8000)      │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └──────────────────────┴──────────────────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        │                                                  │
        │         CORE AI CHATBOT API (FastAPI)           │
        │                                                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │          API LAYER (v1)                  │  │
        │  │  ┌────────────┐  ┌─────────┐  ┌───────┐ │  │
        │  │  │Conversations│  │  Chat   │  │Health │ │  │
        │  │  │ Endpoints  │  │Endpoints│  │Checks │ │  │
        │  │  └─────┬──────┘  └────┬────┘  └───┬───┘ │  │
        │  └────────┼──────────────┼───────────┼─────┘  │
        │           │              │           │         │
        │  ┌────────┼──────────────┼───────────┼─────┐  │
        │  │        │    MIDDLEWARE LAYER      │     │  │
        │  │ ┌──────▼───┐  ┌───────▼────┐ ┌───▼───┐ │  │
        │  │ │  Error   │  │   Rate     │ │Request│ │  │
        │  │ │ Handler  │  │  Limiter   │ │Logger │ │  │
        │  │ └──────────┘  └────────────┘ └───────┘ │  │
        │  └──────────────────┬──────────────────────┘  │
        │                     │                          │
        │  ┌──────────────────▼──────────────────────┐  │
        │  │         SERVICE LAYER                   │  │
        │  │  ┌────────────────┐  ┌───────────────┐ │  │
        │  │  │ Conversation   │  │  AI Service   │ │  │
        │  │  │    Service     │◄─┤  (Mistral)    │ │  │
        │  │  └───────┬────────┘  └───────┬───────┘ │  │
        │  └──────────┼─────────────────┬─┼─────────┘  │
        │             │                 │ │             │
        │  ┌──────────▼─────────────────▼─▼─────────┐  │
        │  │       REPOSITORY LAYER                  │  │
        │  │  ┌─────────────┐  ┌──────────────────┐ │  │
        │  │  │Conversation │  │     Message      │ │  │
        │  │  │ Repository  │  │   Repository     │ │  │
        │  │  └──────┬──────┘  └────────┬─────────┘ │  │
        │  └─────────┼──────────────────┼───────────┘  │
        │            │                  │               │
        │  ┌─────────▼──────────────────▼───────────┐  │
        │  │         DATABASE LAYER                  │  │
        │  │  ┌───────────────────────────────────┐ │  │
        │  │  │      SQLAlchemy ORM (Async)       │ │  │
        │  │  └───────────────┬───────────────────┘ │  │
        │  └──────────────────┼─────────────────────┘  │
        └───────────────────┬─┼─────────────────────────┘
                            │ │
        ┌───────────────────┘ └────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌────────────────────┐
│  PRIMARY DATABASE │                    │   EXTERNAL APIs    │
│                   │                    │                    │
│  PostgreSQL / DB  │                    │   Mistral AI API   │
│    (Port 5432)    │                    │   (api.mistral.ai) │
└─────────┬─────────┘                    └────────────────────┘
          │
          ├─────────────────┐
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌─────────────────┐
│  Redis Cache     │  │  Backup Store   │
│  (Port 6379)     │  │  (S3 / Blob)    │
└──────────────────┘  └─────────────────┘
```

---

## Detailed Component Architecture

### 1. API Layer (Presentation)

```
┌────────────────────────────────────────────────────────┐
│                    API LAYER (v1)                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  /api/v1/conversations                                 │
│  ├── GET    /               → List conversations      │
│  ├── POST   /               → Create conversation     │
│  ├── GET    /{id}           → Get conversation        │
│  ├── PUT    /{id}           → Update conversation     │
│  ├── DELETE /{id}           → Delete conversation     │
│  └── POST   /{id}/clear     → Clear messages          │
│                                                        │
│  /api/v1/chat                                         │
│  ├── POST   /               → Send message            │
│  └── POST   /stream         → Send message (SSE)      │
│                                                        │
│  /api/v1/health                                       │
│  ├── GET    /               → App health              │
│  ├── GET    /db             → Database health         │
│  └── GET    /ai             → AI service health       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 2. Service Layer (Business Logic)

```
┌────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ConversationService                                   │
│  ├── create_conversation()                            │
│  ├── send_message()                                   │
│  ├── stream_message()                                 │
│  └── get_conversation_history()                       │
│                                                        │
│  AIService (Mistral Integration)                      │
│  ├── chat_completion()                                │
│  ├── chat_completion_stream()                         │
│  ├── prepare_messages()                               │
│  └── generate_title()                                 │
│                                                        │
│  AuthService (Future)                                 │
│  ├── login()                                          │
│  ├── register()                                       │
│  ├── refresh_token()                                  │
│  └── validate_token()                                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 3. Repository Layer (Data Access)

```
┌────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  BaseRepository<T>                                     │
│  ├── get_by_id()                                      │
│  ├── get_all()                                        │
│  ├── create()                                         │
│  ├── update()                                         │
│  ├── delete()                                         │
│  └── count()                                          │
│                                                        │
│  ConversationRepository extends BaseRepository        │
│  ├── get_with_messages()                             │
│  ├── get_by_user()                                   │
│  ├── search_conversations()                          │
│  └── get_conversation_stats()                        │
│                                                        │
│  MessageRepository extends BaseRepository             │
│  ├── get_by_conversation()                           │
│  ├── create_message()                                │
│  ├── get_last_n_messages()                           │
│  └── get_token_usage()                               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Chat Message Flow (Non-Streaming)

```
┌────────┐       ┌─────────┐       ┌──────────┐       ┌────────────┐
│ Client │──1──→ │   API   │──2──→ │ Service  │──3──→ │ Repository │
└────────┘       │ Layer   │       │  Layer   │       │   Layer    │
    ▲            └─────────┘       └──────────┘       └────────────┘
    │                 │                  │                    │
    │                 │                  │                    ▼
    │                 │                  │            ┌────────────┐
    │                 │                  │            │  Database  │
    │                 │                  │            └────────────┘
    │                 │                  │                    │
    │                 │                  ▼                    │
    │                 │            ┌──────────┐              │
    │                 │            │    AI    │              │
    │                 │            │ Service  │              │
    │                 │            │(Mistral) │              │
    │                 │            └──────────┘              │
    │                 │                  │                   │
    │                 │                  │                   │
    │                 │            ┌─────▼────┐              │
    │                 │            │ External │              │
    │                 │            │Mistral AI│              │
    │                 │            └──────────┘              │
    │                 │                  │                   │
    └────────8────────┴─────────7────────┴──────────6────────┘

Steps:
1. Client sends POST /chat request
2. API validates and forwards to Service
3. Service fetches conversation from Repository
4. Repository retrieves from Database
5. Service prepares messages and calls AI Service
6. AI Service calls Mistral API
7. Service saves response via Repository
8. API returns response to Client
```

### Streaming Message Flow

```
┌────────┐                                              ┌──────────┐
│ Client │◄────────SSE Connection (EventSource)────────┤   API    │
└────────┘                                              │  Layer   │
    ▲                                                   └────┬─────┘
    │                                                        │
    │  ┌──────────────────────────────────────────────┐    │
    │  │ {"type":"conversation_id","id":"123"}        │◄───┤
    │  │ {"type":"content","text":"Hello"}            │    │
    │  │ {"type":"content","text":" there"}           │    │
    │  │ {"type":"content","text":"!"}                │    │
    │  │ {"type":"done"}                              │    │
    │  └──────────────────────────────────────────────┘    │
    │                                                       │
    │                                              ┌────────▼────────┐
    │                                              │  AI Service     │
    └──────────────────────────────────────────── │  (Streaming)    │
                                                   └─────────────────┘
                                                           │
                                                    Async Generator
                                                           │
                                                   ┌───────▼────────┐
                                                   │  Mistral API   │
                                                   │   (Streaming)  │
                                                   └────────────────┘
```

---

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                       conversations                         │
├─────────────────────────────────────────────────────────────┤
│ id                  VARCHAR(36)   PRIMARY KEY              │
│ title               VARCHAR(200)  NOT NULL                 │
│ system_prompt       TEXT          NULL                     │
│ user_id             VARCHAR(36)   NULL        INDEX        │
│ created_at          TIMESTAMP     NOT NULL    INDEX        │
│ updated_at          TIMESTAMP     NOT NULL    INDEX        │
│ is_deleted          INTEGER       DEFAULT 0   INDEX        │
│ message_count       INTEGER       DEFAULT 0                │
│ temperature         VARCHAR(10)   NULL                     │
│ max_tokens          INTEGER       NULL                     │
│ model_name          VARCHAR(100)  NULL                     │
│ metadata            JSON          NULL                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ One-to-Many
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         messages                            │
├─────────────────────────────────────────────────────────────┤
│ id                  VARCHAR(36)   PRIMARY KEY              │
│ conversation_id     VARCHAR(36)   FOREIGN KEY  INDEX       │
│ role                VARCHAR(20)   NOT NULL     INDEX       │
│ content             TEXT          NOT NULL                 │
│ created_at          TIMESTAMP     NOT NULL     INDEX       │
│ prompt_tokens       INTEGER       NULL                     │
│ completion_tokens   INTEGER       NULL                     │
│ total_tokens        INTEGER       NULL                     │
│ model_name          VARCHAR(100)  NULL                     │
│ finish_reason       VARCHAR(50)   NULL                     │
│ processing_time_ms  INTEGER       NULL                     │
│ metadata            JSON          NULL                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                          users                              │
├─────────────────────────────────────────────────────────────┤
│ id                  VARCHAR(36)   PRIMARY KEY              │
│ email               VARCHAR(255)  UNIQUE     INDEX         │
│ username            VARCHAR(100)  UNIQUE     INDEX         │
│ hashed_password     VARCHAR(255)  NOT NULL                 │
│ full_name           VARCHAR(200)  NULL                     │
│ is_active           INTEGER       DEFAULT 1                │
│ is_verified         INTEGER       DEFAULT 0                │
│ created_at          TIMESTAMP     NOT NULL                 │
│ updated_at          TIMESTAMP     NOT NULL                 │
│ last_login          TIMESTAMP     NULL                     │
│ api_key_hash        VARCHAR(255)  UNIQUE     INDEX         │
│ metadata            JSON          NULL                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Layer 1: Network Security                                │
│  ├── HTTPS/TLS Encryption                                │
│  ├── Firewall Rules                                      │
│  └── DDoS Protection                                     │
│                                                            │
│  Layer 2: API Gateway                                     │
│  ├── Rate Limiting                                       │
│  ├── IP Whitelisting                                     │
│  └── Request Throttling                                  │
│                                                            │
│  Layer 3: Authentication                                  │
│  ├── JWT Tokens (Access + Refresh)                      │
│  ├── API Key Validation                                 │
│  └── OAuth2 Support (Future)                            │
│                                                            │
│  Layer 4: Authorization                                   │
│  ├── Role-Based Access Control (RBAC)                   │
│  ├── Resource-Level Permissions                         │
│  └── User Context Validation                            │
│                                                            │
│  Layer 5: Input Validation                               │
│  ├── Pydantic Schema Validation                         │
│  ├── SQL Injection Prevention (ORM)                     │
│  └── XSS Protection                                      │
│                                                            │
│  Layer 6: Data Security                                  │
│  ├── Password Hashing (bcrypt)                          │
│  ├── Encryption at Rest                                 │
│  └── Encrypted Connections                              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Development Environment

```
┌──────────────────────────────────────────┐
│           Developer Machine              │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │  Backend   │      │  Frontend  │    │
│  │ (Port 8000)│      │ (Port 3000)│    │
│  └──────┬─────┘      └────────────┘    │
│         │                                │
│         ▼                                │
│  ┌────────────┐                         │
│  │   SQLite   │                         │
│  └────────────┘                         │
└──────────────────────────────────────────┘
```

### Production Environment (Cloud)

```
                    ┌──────────────────┐
                    │   Cloud CDN      │
                    │  (Static Assets) │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Load Balancer   │
                    │    (ALB/NLB)     │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │Backend 1│         │Backend 2│        │Backend N│
    │Container│         │Container│        │Container│
    └────┬────┘         └────┬────┘        └────┬────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                   │                   │
    ┌────▼─────┐       ┌────▼────┐        ┌────▼────┐
    │PostgreSQL│       │  Redis  │        │   S3    │
    │  Primary │       │  Cache  │        │ Backups │
    └──────────┘       └─────────┘        └─────────┘
         │
         ▼
    ┌──────────┐
    │PostgreSQL│
    │  Replica │
    └──────────┘
```

---

## Technology Stack Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND                                │
│  React 18 + Vite + TailwindCSS + TypeScript                │
└─────────────────────────────────────────────────────────────┘
                             │
                    HTTP/HTTPS (REST)
                             │
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND                                │
│                                                             │
│  Framework:       FastAPI 0.109+                           │
│  Server:          Uvicorn (ASGI)                           │
│  Language:        Python 3.11+                             │
│  ORM:             SQLAlchemy 2.0 (Async)                   │
│  Validation:      Pydantic 2.5+                            │
│  Auth:            JWT (python-jose)                        │
│  Password:        bcrypt (passlib)                         │
│  HTTP Client:     httpx (async)                            │
│  Migrations:      Alembic                                  │
│  Testing:         pytest + pytest-asyncio                  │
│  Code Quality:    black, flake8, mypy, bandit             │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASES                                │
│                                                             │
│  Primary:         PostgreSQL 15+                           │
│  Alternative:     MySQL 8+ / SQLite / MongoDB             │
│  Cache:           Redis 7+                                 │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                          │
│                                                             │
│  AI Provider:     Mistral AI                               │
│  Monitoring:      Sentry (optional)                        │
│  Metrics:         Prometheus + Grafana (optional)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Scalability Architecture

```
                    Load: 1-1000 req/sec
                             │
                    ┌────────▼────────┐
                    │  Single Server  │
                    │  Backend + DB   │
                    └─────────────────┘

                    Load: 1K-10K req/sec
                             │
                    ┌────────▼────────┐
                    │ Load Balancer   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │Backend 1│    │Backend 2│    │Backend 3│
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Database   │
                    │   Primary   │
                    └─────────────┘

                    Load: 10K-100K req/sec
                             │
                    ┌────────▼────────┐
                    │   CDN + WAF     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Load Balancer   │
                    │  (Multi-AZ)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        [Backend] × N   [Backend] × N   [Backend] × N
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │   DB    │    │  Redis  │    │   S3    │
        │ Primary │    │ Cluster │    │(Storage)│
        └────┬────┘    └─────────┘    └─────────┘
             │
        ┌────▼────┐
        │   DB    │
        │ Replica │
        └─────────┘
```

---

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Service 1│  │ Service 2│  │ Service 3│  │ Service N│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   LOGGING    │   │   METRICS    │   │   TRACING    │
│              │   │              │   │              │
│ Structured   │   │ Prometheus   │   │ Request IDs  │
│ JSON Logs    │   │ Counters     │   │ Correlation  │
│ File + Cloud │   │ Histograms   │   │ Performance  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Storage    │   │   Grafana    │   │    Sentry    │
│ ELK / Cloud  │   │  Dashboard   │   │ Error Track  │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

**Legend:**
- `┌─┐` = Component/Service Boundary
- `→` = Synchronous Request/Response
- `↔` = Bidirectional Communication
- `⇄` = Streaming/WebSocket
- `▼` = Data Flow Direction

---

*This architecture supports scalability from 1 to 1,000,000+ users*