# SQL Agent - Text-to-SQL Chatbot

**Transform natural language questions into SQL queries using AI**

This application uses SQLCoder (via Ollama) to convert natural language questions into SQL queries for any database schema.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8+
- Ollama installed (automatically installing...)

### 1. Install Ollama Model

```bash
# Pull the SQLCoder model (one-time, ~4GB download)
ollama pull sqlcoder
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the API Server

```bash
# From the backend directory
uvicorn main:app --reload --port 8000
```

The server will start at `http://localhost:8000`

### 4. Test the API

```bash
# In a new terminal
cd backend
python test_sql_api.py
```

## 📖 API Usage

### Generate SQL from Natural Language

**Endpoint**: `POST /api/v1/sql/generate`

**Request**:
```json
{
  "question": "What are the names of all singers born after 1990?",
  "schema": {
    "name": "music_database",
    "tables": [
      {
        "name": "singer",
        "columns": [
          {"name": "singer_id", "type": "INTEGER", "primary_key": true},
          {"name": "name", "type": "TEXT"},
          {"name": "birth_year", "type": "INTEGER"}
        ],
        "foreign_keys": []
      }
    ]
  }
}
```

**Response**:
```json
{
  "sql": "SELECT name FROM singer WHERE birth_year > 1990",
  "is_valid": true,
  "confidence": 0.9,
  "explanation": "This query filters data to answer: What are the names of all singers born after 1990?",
  "validation_errors": []
}
```

### Validate SQL Query

**Endpoint**: `POST /api/v1/sql/validate`

**Request**:
```json
{
  "sql": "SELECT * FROM users",
  "schema": { /* schema object */ },
  "max_rows": 100
}
```

### Check Health

**Endpoint**: `GET /api/v1/sql/health`

Returns status of SQL agent, Ollama connection, and available models.

## 🛡️ Safety Features

The SQL Agent includes multiple safety layers:

1. **Read-Only Mode**: Only SELECT queries are allowed by default
2. **SQL Injection Prevention**: Detects and blocks common injection patterns
3. **Dangerous Operation Blocking**: Prevents DROP, DELETE without WHERE, etc.
4. **Automatic LIMIT**: Adds row limits to prevent large result sets
5. **Syntax Validation**: Validates SQL syntax before execution

## 🧪 Example Test Cases

```python
# Valid queries - will be accepted
"SELECT name FROM users"
"SELECT * FROM products WHERE price > 100"
"SELECT COUNT(*) FROM orders GROUP BY customer_id"

# Blocked queries - safety violations
"DROP TABLE users"  # Dangerous operation
"DELETE FROM users"  # DELETE without WHERE
"UPDATE products SET price = 0"  # UPDATE without WHERE
```

## 📊 Supported Database Types

The SQL Agent works with any SQL database schema including:
- PostgreSQL
- MySQL
- SQLite
- Microsoft SQL Server
- Oracle

Simply provide the schema structure in the API request.

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# Ollama endpoint
OLLAMA_URL=http://localhost:11434

# Model to use
SQL_MODEL=sqlcoder

# Safety settings
MAX_RESULT_ROWS=100
ALLOW_MODIFICATIONS=false  # Set to true to allow INSERT/UPDATE/DELETE
```

## 🔧 Troubleshooting

### "Ollama is not running"
```bash
# Check if Ollama service is running
ollama list

# If not, Ollama may not be installed or the service isn't started
# Restart your terminal/computer after Ollama installation
```

### "sqlcoder model not found"
```bash
# Pull the model
ollama pull sqlcoder

# Verify it's available
ollama list
```

### "Failed to generate SQL"
- Check that your schema is properly formatted
- Ensure the question is clear and specific
- Try rephrasing the question

## 📈 Performance

- **Inference Time**: 2-5 seconds per query (CPU)
- **Accuracy**: ~75% on Spider benchmark (complex queries)
- **Model Size**: ~4GB (quantized)

## 🎯 Next Steps

1. **Frontend UI**: Build a web interface for the SQL agent
2. **Database Execution**: Add actual database querying
3. **Fine-tuning**: Improve accuracy with domain-specific fine-tuning
4. **Multi-turn Conversations**: Add conversation history support

## 📚 Original Chatbot Features

The original Mistral AI chatbot endpoints are still available:
- `/conversations` - Manage conversations
- `/chat` - Chat with Mistral AI
- `/chat/stream` - Streaming responses

## 🤝 Contributing

See the original README for contribution guidelines.

## 📄 License

MIT License - see LICENSE file
