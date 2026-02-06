"""
Example database schema and test queries for SQL Agent
"""

# Example 1: Simple Music Database
MUSIC_DATABASE_SCHEMA = {
    "name": "music_database",
    "tables": [
        {
            "name": "singer",
            "description": "Information about singers",
            "columns": [
                {"name": "singer_id", "type": "INTEGER", "primary_key": True, "nullable": False},
                {"name": "name", "type": "TEXT", "nullable": False, "description": "Singer's full name"},
                {"name": "birth_year", "type": "INTEGER", "nullable": True, "description": "Year of birth"},
                {"name": "country", "type": "TEXT", "nullable": True, "description": "Country of origin"}
            ],
            "foreign_keys": []
        },
        {
            "name": "song",
            "description": "Songs in the database",
            "columns": [
                {"name": "song_id", "type": "INTEGER", "primary_key": True, "nullable": False},
                {"name": "title", "type": "TEXT", "nullable": False, "description": "Song title"},
                {"name": "singer_id", "type": "INTEGER", "nullable": False, "description": "Singer who performed the song"},
                {"name": "release_year", "type": "INTEGER", "nullable": True, "description": "Year released"},
                {"name": "duration_seconds", "type": "INTEGER", "nullable": True, "description": "Song length in seconds"}
            ],
            "foreign_keys": [
                {"column": "singer_id", "referenced_table": "singer", "referenced_column": "singer_id"}
            ]
        }
    ]
}

# Example test questions
TEST_QUESTIONS = [
    {
        "question": "What are the names of all singers?",
        "expected_sql": "SELECT name FROM singer"
    },
    {
        "question": "List all singers born after 1990",
        "expected_sql": "SELECT name FROM singer WHERE birth_year > 1990"
    },
    {
        "question": "How many songs does each singer have?",
        "expected_sql": "SELECT singer.name, COUNT(song.song_id) as song_count FROM singer LEFT JOIN song ON singer.singer_id = song.singer_id GROUP BY singer.singer_id, singer.name"
    },
    {
        "question": "What are the titles of songs released in 2020?",
        "expected_sql": "SELECT title FROM song WHERE release_year = 2020"
    },
    {
        "question": "Show me the longest songs with their singers",
        "expected_sql": "SELECT song.title, singer.name, song.duration_seconds FROM song JOIN singer ON song.singer_id = singer.singer_id ORDER BY song.duration_seconds DESC"
    }
]

# Example 2: E-commerce Database
ECOMMERCE_SCHEMA = {
    "name": "ecommerce",
    "tables": [
        {
            "name": "customers",
            "columns": [
                {"name": "customer_id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "TEXT"},
                {"name": "email", "type": "TEXT"},
                {"name": "join_date", "type": "DATE"}
            ],
            "foreign_keys": []
        },
        {
            "name": "orders",
            "columns": [
                {"name": "order_id", "type": "INTEGER", "primary_key": True},
                {"name": "customer_id", "type": "INTEGER"},
                {"name": "order_date", "type": "DATE"},
                {"name": "total_amount", "type": "REAL"}
            ],
            "foreign_keys": [
                {"column": "customer_id", "referenced_table": "customers", "referenced_column": "customer_id"}
            ]
        },
        {
            "name": "products",
            "columns": [
                {"name": "product_id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "TEXT"},
                {"name": "price", "type": "REAL"},
                {"name": "stock_quantity", "type": "INTEGER"}
            ],
            "foreign_keys": []
        }
    ]
}

ECOMMERCE_QUESTIONS = [
    {
        "question": "Show me all customers who joined in 2024",
        "expected_sql": "SELECT * FROM customers WHERE join_date >= '2024-01-01' AND join_date < '2025-01-01'"
    },
    {
        "question": "What is the total number of orders?",
        "expected_sql": "SELECT COUNT(*) as total_orders FROM orders"
    },
    {
        "question": "List products that are out of stock",
        "expected_sql": "SELECT name FROM products WHERE stock_quantity = 0"
    }
]

if __name__ == "__main__":
    print("Example Database Schemas and Test Questions")
    print("=" * 60)
    print("\n1. Music Database Schema:")
    print(f"   - Tables: {len(MUSIC_DATABASE_SCHEMA['tables'])}")
    print(f"   - Test Questions: {len(TEST_QUESTIONS)}")
    print("\n2. E-commerce Database Schema:")
    print(f"   - Tables: {len(ECOMMERCE_SCHEMA['tables'])}")
    print(f"   - Test Questions: {len(ECOMMERCE_QUESTIONS)}")
