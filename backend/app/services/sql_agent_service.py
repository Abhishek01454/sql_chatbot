"""
SQL Agent Service - Generates SQL from natural language using Ollama + SQLCoder
"""
import httpx
import logging
from typing import Optional
from app.schemas.sql_schemas import (
    SQLRequest, SQLResponse, DatabaseSchema, ValidationError
)
from app.utils.sql_safety import SQLSafetyValidator

logger = logging.getLogger(__name__)


class SQLAgentService:
    """Service for generating SQL queries from natural language"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "sqlcoder"  # Will pull this model via Ollama
        self.safety_validator = SQLSafetyValidator()
    
    async def generate_sql(
        self,
        question: str,
        schema: DatabaseSchema,
        conversation_history: Optional[list] = None
    ) -> SQLResponse:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            schema: Database schema
            conversation_history: Optional conversation history for context
            
        Returns:
            SQLResponse with generated SQL and validation results
        """
        try:
            # Build prompt with schema context
            prompt = self._build_prompt(question, schema, conversation_history)
            
            # Call Ollama API
            generated_sql = await self._call_ollama(prompt)
            
            # Extract SQL from response (remove markdown, explanations, etc.)
            sql = self._extract_sql(generated_sql)
            
            # Validate SQL safety
            is_valid, errors = self.safety_validator.validate(sql, strict_mode=True)
            
            # Format SQL
            if is_valid:
                sql = self.safety_validator.format_sql(sql)
                sql = self.safety_validator.sanitize_sql(sql, max_rows=100)
            
            # Generate explanation (optional)
            explanation = self._generate_explanation(sql, question)
            
            return SQLResponse(
                sql=sql,
                explanation=explanation,
                is_valid=is_valid,
                validation_errors=errors,
                confidence=0.9 if is_valid else 0.5
            )
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return SQLResponse(
                sql="",
                explanation=None,
                is_valid=False,
                validation_errors=[
                    ValidationError(
                        error_type="generation_error",
                        message=f"Failed to generate SQL: {str(e)}",
                        severity="critical"
                    )
                ],
                confidence=0.0
            )
    
    def _build_prompt(
        self,
        question: str,
        schema: DatabaseSchema,
        conversation_history: Optional[list] = None
    ) -> str:
        """Build prompt for SQL generation"""
        # SQLCoder-specific prompt format (following defog.ai recommendations)
        prompt = f"""### Task
Generate a SQL query to answer the following question: `{question}`

### Database Schema
{schema.to_prompt_format()}

### Answer
Given the database schema, here is the SQL query that answers `{question}`:
```sql
"""
        return prompt
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for SQL generation"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic SQL generation
                        "top_p": 0.95,
                        "num_predict": 200,  # Limit tokens
                        "stop": ["```", "\n\n\n"]  # Stop at code block end
                    }
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")
            
            result = response.json()
            return result.get("response", "")
    
    def _extract_sql(self, generated_text: str) -> str:
        """Extract SQL query from generated text"""
        text = generated_text.strip()
        
        # Remove any leading/trailing special tokens
        text = text.replace("<s>", "").replace("</s>", "").strip()
        
        # Remove markdown code blocks
        if "```sql" in text:
            # Extract content between ```sql and ```
            start = text.find("```sql") + 6
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif text.startswith("```"):
            text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
        
        # Clean up
        text = text.strip()
        
        # Handle multiple lines - find the SELECT statement
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Look for SELECT statement
        for i, line in enumerate(lines):
            if line.upper().startswith('SELECT'):
                # Join this line and subsequent lines until we hit a semicolon or end
                sql_lines = [line]
                for next_line in lines[i+1:]:
                    sql_lines.append(next_line)
                    if next_line.endswith(';'):
                        break
                return ' '.join(sql_lines).strip()
        
        # If no SELECT found, return first meaningful line
        if lines:
            return lines[0]
        
        return text
    
    def _generate_explanation(self, sql: str, question: str) -> str:
        """Generate simple explanation of the SQL query"""
        # Basic explanation based on SQL structure
        if "JOIN" in sql.upper():
            return f"This query joins multiple tables to answer: {question}"
        elif "GROUP BY" in sql.upper():
            return f"This query aggregates data to answer: {question}"
        elif "WHERE" in sql.upper():
            return f"This query filters data to answer: {question}"
        else:
            return f"This query retrieves data to answer: {question}"
    
    async def validate_sql(
        self,
        sql: str,
        schema: DatabaseSchema
    ) -> SQLResponse:
        """
        Validate SQL query against schema and safety rules
        
        Args:
            sql: SQL query to validate
            schema: Database schema
            
        Returns:
            SQLResponse with validation results
        """
        is_valid, errors = self.safety_validator.validate(sql, strict_mode=True)
        
        return SQLResponse(
            sql=sql,
            explanation=None,
            is_valid=is_valid,
            validation_errors=errors,
            confidence=1.0 if is_valid else 0.0
        )
