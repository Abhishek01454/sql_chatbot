"""
Quick test script for SQL Agent API
Run this after starting the FastAPI server
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Example database schema
MUSIC_SCHEMA = {
    "name": "music_database",
    "tables": [
        {
            "name": "singer",
            "description": "Information about singers",
            "columns": [
                {"name": "singer_id", "type": "INTEGER", "primary_key": True, "nullable": False},
                {"name": "name", "type": "TEXT", "nullable": False},
                {"name": "birth_year", "type": "INTEGER", "nullable": True},
                {"name": "country", "type": "TEXT", "nullable": True}
            ],
            "foreign_keys": []
        },
        {
            "name": "song",
            "description": "Songs in the database",
            "columns": [
                {"name": "song_id", "type": "INTEGER", "primary_key": True, "nullable": False},
                {"name": "title", "type": "TEXT", "nullable": False},
                {"name": "singer_id", "type": "INTEGER", "nullable": False},
                {"name": "release_year", "type": "INTEGER", "nullable": True}
            ],
            "foreign_keys": [
                {"column": "singer_id", "referenced_table": "singer", "referenced_column": "singer_id"}
            ]
        }
    ]
}

def test_health():
    """Test SQL agent health endpoint"""
    print("\n" + "="*60)
    print("Testing SQL Agent Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/sql/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_sql_generation():
    """Test SQL generation from natural language"""
    print("\n" + "="*60)
    print("Testing SQL Generation")
    print("="*60)
    
    test_questions = [
        "What are the names of all singers?",
        "List all singers born after 1990",
        "How many songs does each singer have?",
        "Show me songs released in 2020"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 60)
        
        payload = {
            "question": question,
            "schema": MUSIC_SCHEMA,
            "execute": False
        }
        
        try:
            response = requests.post(f"{BASE_URL}/sql/generate", json=payload)
            result = response.json()
            
            print(f"Generated SQL: {result.get('sql', 'N/A')}")
            print(f"Valid: {result.get('is_valid', False)}")
            print(f"Confidence: {result.get('confidence', 0)}")
            
            if result.get('validation_errors'):
                print(f"Validation Errors: {result['validation_errors']}")
            
            if result.get('explanation'):
                print(f"Explanation: {result['explanation']}")
                
        except Exception as e:
            print(f"Error: {e}")

def test_sql_validation():
    """Test SQL validation"""
    print("\n" + "="*60)
    print("Testing SQL Validation")
    print("="*60)
    
    test_cases = [
        ("SELECT * FROM singer", True, "Valid SELECT query"),
        ("DROP TABLE singer", False, "Dangerous DROP operation"),
        ("DELETE FROM singer WHERE singer_id = 1", True, "DELETE with WHERE"),
        ("DELETE FROM singer", False, "DELETE without WHERE"),
        ("SELECT name FROM singer; DROP TABLE song", False, "SQL injection attempt")
    ]
    
    for sql, should_be_valid, description in test_cases:
        print(f"\n{description}")
        print(f"SQL: {sql}")
        print("-" * 60)
        
        payload = {
            "sql": sql,
            "schema": MUSIC_SCHEMA,
            "max_rows": 100
        }
        
        try:
            response = requests.post(f"{BASE_URL}/sql/validate", json=payload)
            result = response.json()
            
            is_valid = result.get('is_valid', False)
            print(f"Valid: {is_valid} (Expected: {should_be_valid})")
            
            if result.get('validation_errors'):
                for error in result['validation_errors']:
                    print(f"  - {error['severity'].upper()}: {error['message']}")
            
            if is_valid == should_be_valid:
                print("✓ Test PASSED")
            else:
                print("✗ Test FAILED")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SQL AGENT API TEST SUITE")
    print("="*60)
    print("\nMake sure the FastAPI server is running:")
    print("  cd backend && uvicorn main:app --reload")
    print("\nAnd Ollama is running with sqlcoder model:")
    print("  ollama pull sqlcoder")
    
    # Run tests
    if test_health():
        test_sql_generation()
        test_sql_validation()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETE")
        print("="*60)
    else:
        print("\n⚠️  Health check failed. Please ensure:")
        print("  1. FastAPI server is running (uvicorn main:app --reload)")
        print("  2. Ollama is installed and running")
        print("  3. SQLCoder model is pulled (ollama pull sqlcoder)")
