"""
SQL safety validation utilities
Prevents dangerous SQL operations and ensures query safety
"""
import re
import sqlparse
from typing import Tuple, List
from app.schemas.sql_schemas import ValidationError


class SQLSafetyValidator:
    """Validates SQL queries for safety and security"""
    
    # Dangerous keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        r'\bDROP\s+TABLE\b',
        r'\bDROP\s+DATABASE\b',
        r'\bTRUNCATE\b',
        r'\bDELETE\s+FROM\b(?!\s+\w+\s+WHERE)',  # DELETE without WHERE
        r'\bUPDATE\s+\w+\s+SET\b(?!.*WHERE)',     # UPDATE without WHERE
        r'\bCREATE\s+TABLE\b',
        r'\bALTER\s+TABLE\b',
        r'\bGRANT\b',
        r'\bREVOKE\b',
        r'\bEXEC\b',
        r'\bEXECUTE\b',
        r';\s*DROP',  # SQL injection attempt
        r'--',  # Comment injection
        r'/\*',  # Block comment injection
    ]
    
   
 # Allowed operations (whitelist)
    ALLOWED_OPERATIONS = ['SELECT']
    
    @staticmethod
    def validate(sql: str, strict_mode: bool = True) -> Tuple[bool, List[ValidationError]]:
        """
        Validate SQL query for safety
        
        Args:
            sql: SQL query to validate
            strict_mode: If True, only allow SELECT statements
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for empty query
        if not sql or not sql.strip():
            errors.append(ValidationError(
                error_type="empty_query",
                message="SQL query is empty",
                severity="error"
            ))
            return False, errors
        
        # Parse SQL
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                errors.append(ValidationError(
                    error_type="parse_error",
                    message="Failed to parse SQL query",
                    severity="error"
                ))
                return False, errors
        except Exception as e:
            errors.append(ValidationError(
                error_type="syntax_error",
                message=f"SQL syntax error: {str(e)}",
                severity="error"
            ))
            return False, errors
        
        # Check for dangerous keywords
        sql_upper = sql.upper()
        for pattern in SQLSafetyValidator.DANGEROUS_KEYWORDS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                errors.append(ValidationError(
                    error_type="dangerous_operation",
                    message=f"Dangerous SQL operation detected: {pattern}",
                    severity="critical"
                ))
        
        # Check if only SELECT operations in strict mode
        if strict_mode:
            statement = parsed[0]
            stmt_type = statement.get_type()
            if stmt_type != 'SELECT':
                errors.append(ValidationError(
                    error_type="forbidden_operation",
                    message=f"Only SELECT queries are allowed. Found: {stmt_type}",
                    severity="error"
                ))
        
        # Check for multiple statements (potential SQL injection)
        if len(parsed) > 1:
            errors.append(ValidationError(
                error_type="multiple_statements",
                message="Multiple SQL statements detected. Only single queries allowed.",
                severity="critical"
            ))
        
        # Validation passed if no critical/error severity issues
        critical_errors = [e for e in errors if e.severity in ["error", "critical"]]
        is_valid = len(critical_errors) == 0
        
        return is_valid, errors
    
    @staticmethod
    def add_limit_clause(sql: str, max_rows: int = 100) -> str:
        """
        Add LIMIT clause to SQL if not present
        
        Args:
            sql: SQL query
            max_rows: Maximum number of rows to return
            
        Returns:
            SQL with LIMIT clause
        """
        sql = sql.strip().rstrip(';')
        
        # Check if LIMIT already exists
        if re.search(r'\bLIMIT\s+\d+', sql, re.IGNORECASE):
            return sql
        
        # Add LIMIT
        return f"{sql} LIMIT {max_rows}"
    
    @staticmethod
    def sanitize_sql(sql: str, max_rows: int = 100) -> str:
        """
        Sanitize SQL query by adding safety measures
        
        Args:
            sql: SQL query to sanitize
            max_rows: Maximum rows to return
            
        Returns:
            Sanitized SQL
        """
        # Remove trailing semicolons
        sql = sql.strip().rstrip(';')
        
        # Add LIMIT if SELECT statement
        if sql.upper().startswith('SELECT'):
            sql = SQLSafetyValidator.add_limit_clause(sql, max_rows)
        
        return sql
    
    @staticmethod
    def format_sql(sql: str) -> str:
        """
        Format SQL for better readability
        
        Args:
            sql: SQL query to format
            
        Returns:
            Formatted SQL
        """
        try:
            return sqlparse.format(
                sql,
                reindent=True,
                keyword_case='upper',
                strip_comments=True
            )
        except:
            return sql
