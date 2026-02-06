"""
SQL generation API endpoints
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from pathlib import Path
from app.schemas.sql_schemas import (
    SQLRequest, SQLResponse, SQLExecuteRequest, SQLExecuteResponse
)
from app.services.sql_agent_service import SQLAgentService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sql", tags=["SQL Agent"])

# Initialize SQL agent service
sql_agent = SQLAgentService()


@router.post("/generate", response_model=SQLResponse)
async def generate_sql(request: SQLRequest):
    """
    Generate SQL query from natural language
    
    Args:
        request: SQL generation request with question and schema
        
    Returns:
        SQLResponse with generated SQL and validation results
    """
    try:
        logger.info(f"Generating SQL for question: {request.question}")
        
        response = await sql_agent.generate_sql(
            question=request.question,
            schema=request.schema,
            conversation_history=None  # TODO: Load from conversation_id if provided
        )
        
        logger.info(f"Generated SQL: {response.sql}, Valid: {response.is_valid}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in generate_sql endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SQL: {str(e)}"
        )


@router.post("/validate", response_model=SQLResponse)
async def validate_sql(request: SQLExecuteRequest):
    """
    Validate SQL query for safety and syntax
    
    Args:
        request: SQL validation request
        
    Returns:
        SQLResponse with validation results
    """
    try:
        logger.info(f"Validating SQL: {request.sql[:100]}...")
        
        response = await sql_agent.validate_sql(
            sql=request.sql,
            schema=request.schema
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in validate_sql endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate SQL: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Check if SQL agent service is healthy
    
    Returns:
        Health status including Ollama connectivity
    """
    try:
        # Check if Ollama is accessible
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{sql_agent.ollama_url}/api/tags")
            ollama_healthy = response.status_code == 200
            models = response.json().get("models", []) if ollama_healthy else []
            
            # Check if sqlcoder model is available
            sqlcoder_available = any(
                model.get("name", "").startswith("sqlcoder") 
                for model in models
            )
            
            return {
                "status": "healthy" if ollama_healthy else "degraded",
                "ollama_connected": ollama_healthy,
                "sqlcoder_available": sqlcoder_available,
                "available_models": [m.get("name") for m in models],
                "message": "SQL Agent is ready" if sqlcoder_available else "Please pull sqlcoder model: ollama pull sqlcoder"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "sqlcoder_available": False,
            "error": str(e),
            "message": "Ollama is not running. Please start Ollama service."
        }


@router.post("/extract-schema")
async def extract_schema_from_file(file: UploadFile = File(...)):
    """
    Extract database schema from uploaded SQLite file
    
    Args:
        file: Uploaded database file (.db, .sqlite, .sqlite3)
        
    Returns:
        DatabaseSchema extracted from the file
    """
    import tempfile
    import os
    from app.utils.schema_extractor import SchemaExtractor
    
    # Validate file extension
    allowed_extensions = [
        ".db", ".sqlite", ".sqlite3",  # SQLite
        ".xlsx", ".xls",                # Excel
        ".csv",                         # CSV
        ".sql",                         # SQL dumps
        ".json"                         # JSON
    ]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Extract schema (auto-detects file type)
        logger.info(f"Extracting schema from: {file.filename}")
        
        # Use original filename for proper database name extraction
        schema = SchemaExtractor.extract_schema_auto(temp_path)
        # Override with original filename
        schema.name = Path(file.filename).stem
        
        # Get additional info
        info = SchemaExtractor.get_schema_info(temp_path)
        
        logger.info(f"Extracted {info['table_count']} tables with {info['total_columns']} columns")
        
        return {
            "schema": schema,
            "info": info,
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error extracting schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract schema: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
