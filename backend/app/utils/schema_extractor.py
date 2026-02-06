"""
Database schema extraction utilities
Extracts schema from multiple file formats: SQLite, Excel, CSV, SQL dumps, JSON
"""
import sqlite3
import json
import re
from typing import Dict, List
from pathlib import Path
from app.schemas.sql_schemas import DatabaseSchema, Table, Column, ForeignKey


class SchemaExtractor:
    """Extract database schema from various file formats"""
    
    @staticmethod
    def _infer_type_from_pandas_dtype(dtype_str: str, sample_values=None) -> str:
        """Infer SQL type from pandas dtype with better accuracy"""
        dtype_str = str(dtype_str).lower()
        
        # Check pandas dtype first
        if 'int' in dtype_str:
            return "INTEGER"
        elif 'float' in dtype_str or 'double' in dtype_str:
            return "REAL"
        elif 'bool' in dtype_str:
            return "BOOLEAN"
        elif 'datetime' in dtype_str or 'date' in dtype_str:
            return "DATETIME"
        elif 'object' in dtype_str or 'string' in dtype_str:
            # For object types, check sample values
            if sample_values is not None and len(sample_values) > 0:
                # Check if all non-null values are numeric
                try:
                    non_null = [v for v in sample_values if v is not None and str(v).strip()]
                    if non_null:
                        # Try to convert to numeric
                        numeric_vals = [float(str(v).replace(',', '')) for v in non_null[:10]]
                        # Check if they're all integers
                        if all(v.is_integer() for v in numeric_vals):
                            return "INTEGER"
                        else:
                            return "REAL"
                except (ValueError, AttributeError):
                    pass
            return "TEXT"
        else:
            return "TEXT"
    
    @staticmethod
    def _infer_type_from_value(value) -> str:
        """Infer SQL type from Python value (fallback method)"""
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, str):
            # Check if it looks like a date
            if re.match(r'\d{4}-\d{2}-\d{2}', str(value)):
                return "DATE"
            return "TEXT"
        else:
            return "TEXT"
    
    @staticmethod
    def extract_from_sqlite(db_path: str) -> DatabaseSchema:
        """Extract schema from SQLite database file"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        db_name = Path(db_path).stem
        tables = []
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = cursor.fetchall()
        
        for (table_name,) in table_names:
            # Get table info
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns_info = cursor.fetchall()
            
            columns = []
            for col in columns_info:
                columns.append(Column(
                    name=col[1],
                    type=col[2] or "TEXT",
                    primary_key=bool(col[5]),
                    nullable=not bool(col[3]),
                    description=None
                ))
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
            fk_info = cursor.fetchall()
            
            foreign_keys = []
            for fk in fk_info:
                foreign_keys.append(ForeignKey(
                    column=fk[3],
                    referenced_table=fk[2],
                    referenced_column=fk[4]
                ))
            
            tables.append(Table(
                name=table_name,
                description=None,
                columns=columns,
                foreign_keys=foreign_keys
            ))
        
        conn.close()
        return DatabaseSchema(name=db_name, tables=tables)
    
    @staticmethod
    def extract_from_excel(file_path: str) -> DatabaseSchema:
        """Extract schema from Excel file - each sheet becomes a table"""
        import pandas as pd
        
        db_name = Path(file_path).stem
        excel_file = pd.ExcelFile(file_path)
        tables = []
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=100)
            
            if df.empty:
                continue
                
            columns = []
            for col_name in df.columns:
                # Get dtype and sample values
                col_type = SchemaExtractor._infer_type_from_pandas_dtype(
                    df[col_name].dtype,
                    df[col_name].dropna().head(10).tolist()
                )
                
                columns.append(Column(
                    name=str(col_name),
                    type=col_type,
                    primary_key=(col_name.lower() in ['id', f'{sheet_name.lower()}_id']),
                    nullable=df[col_name].isnull().any(),
                    description=None
                ))
            
            tables.append(Table(
                name=sheet_name,
                description=f"Imported from Excel sheet: {sheet_name}",
                columns=columns,
                foreign_keys=[]
            ))
        
        return DatabaseSchema(name=db_name, tables=tables)
    
    @staticmethod
    def extract_from_csv(file_path: str) -> DatabaseSchema:
        """Extract schema from CSV file - file becomes a single table"""
        import pandas as pd
        
        db_name = Path(file_path).stem
        df = pd.read_csv(file_path, nrows=100)
        
        columns = []
        for col_name in df.columns:
            col_type = SchemaExtractor._infer_type_from_pandas_dtype(
                df[col_name].dtype,
                df[col_name].dropna().head(10).tolist()
            )
            
            columns.append(Column(
                name=str(col_name),
                type=col_type,
                primary_key=(col_name.lower() in ['id', f'{db_name.lower()}_id']),
                nullable=df[col_name].isnull().any(),
                description=None
            ))
        
        table = Table(
            name=db_name,
            description=f"Imported from CSV file: {Path(file_path).name}",
            columns=columns,
            foreign_keys=[]
        )
        
        return DatabaseSchema(name=db_name, tables=[table])
    
    @staticmethod
    def _split_columns(columns_def: str) -> List[str]:
        """Split column definitions by comma, ignoring commas in parentheses"""
        results = []
        current = []
        paren_depth = 0
        quote = None
        
        for char in columns_def:
            if quote:
                if char == quote:
                    quote = None
                current.append(char)
            else:
                if char in '"\'`':
                    quote = char
                    current.append(char)
                elif char == '(':
                    paren_depth += 1
                    current.append(char)
                elif char == ')':
                    paren_depth -= 1
                    current.append(char)
                elif char == ',' and paren_depth == 0:
                    results.append("".join(current).strip())
                    current = []
                else:
                    current.append(char)
        
        if current:
            results.append("".join(current).strip())
            
        return results

    @staticmethod
    def extract_from_sql(file_path: str) -> DatabaseSchema:
        """Extract schema from SQL dump file by parsing CREATE TABLE statements"""
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        db_name = Path(file_path).stem
        tables = []
        
        # Find all CREATE TABLE statements (improved regex)
        # Handle cases like CREATE TABLE "name" or CREATE TABLE IF NOT EXISTS name
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\(\s]+)\s*\((.*?)\);'
        matches = re.finditer(create_table_pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            # Clean table name
            table_name = match.group(1).strip('`"\'').strip()
            columns_def = match.group(2)
            
            columns = []
            foreign_keys = []
            
            # Parse column definitions
            column_lines = SchemaExtractor._split_columns(columns_def)
            
            for line in column_lines:
                line = line.strip()
                if not line:
                    continue
                
                upper_line = line.upper()
                
                # Check for table-level constraints using regex to avoid partial matches
                # e.g. avoid matching "check_amount" as "CHECK" constraint
                constraint_pattern = r'^\s*(CONSTRAINT|PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CHECK|INDEX)\b'
                if re.match(constraint_pattern, upper_line):
                    # Check for FOREIGN KEY
                    if 'FOREIGN KEY' in upper_line and 'REFERENCES' in upper_line:
                        try:
                            # Format: FOREIGN KEY (col) REFERENCES table(col)
                            fk_match = re.search(r'FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s+(\w+)\s*\((.*?)\)', line, re.IGNORECASE)
                            if fk_match:
                                fk_col = fk_match.group(1).strip('`"\' ')
                                ref_table = fk_match.group(2).strip('`"\' ')
                                ref_col = fk_match.group(3).strip('`"\' ')
                                foreign_keys.append(ForeignKey(
                                    column=fk_col,
                                    referenced_table=ref_table,
                                    referenced_column=ref_col
                                ))
                        except Exception:
                            pass
                    continue
                
                # Parse column: name type constraints
                # Split by space but handle quotes? 
                # Simple approach: name is first word, type is second
                parts = line.split(None, 2) # Split into max 3 parts: name, type, rest
                
                if len(parts) >= 2:
                    col_name = parts[0].strip('`"\'')
                    
                    # If name is a keyword (unlikely if quoted, but possible if not)
                    # Ideally we trust the first token is name unless it is a keyword like CONSTRAINT
                    
                    col_type_raw = parts[1]
                    remaining = parts[2] if len(parts) > 2 else ""
                    remaining_upper = remaining.upper()
                    
                    # Enhanced type mapping
                    col_type_upper = col_type_raw.upper()
                    if 'INT' in col_type_upper:
                        col_type = 'INTEGER'
                    elif any(t in col_type_upper for t in ['CHAR', 'TEXT', 'VARCHAR', 'CLOB']):
                        col_type = 'TEXT'
                    elif any(t in col_type_upper for t in ['REAL', 'FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC']):
                        col_type = 'REAL'
                    elif 'BOOL' in col_type_upper:
                        col_type = 'BOOLEAN'
                    elif 'DATE' in col_type_upper or 'TIME' in col_type_upper:
                        col_type = 'DATETIME'
                    elif 'BLOB' in col_type_upper or 'BINARY' in col_type_upper:
                        col_type = 'BLOB'
                    else:
                        col_type = 'TEXT' # Fallback
                    
                    # Check constraints in the remaining part
                    is_pk = 'PRIMARY KEY' in remaining_upper or 'PRIMARY KEY' in line.upper().replace(col_name.upper(), '', 1) 
                    
                    # Careful: "PRIMARY KEY" might be at table level, but we already handled lines starting with it.
                    # Here we check if "PRIMARY KEY" token exists in the column definition line.
                    # Note: We blindly checked line.upper() before. 
                    
                    is_nullable = 'NOT NULL' not in remaining_upper
                    
                    columns.append(Column(
                        name=col_name,
                        type=col_type,
                        primary_key=is_pk,
                        nullable=is_nullable,
                        description=None
                    ))
            
            if columns:
                tables.append(Table(
                    name=table_name,
                    description=f"Extracted from SQL dump",
                    columns=columns,
                    foreign_keys=foreign_keys
                ))
        
        return DatabaseSchema(name=db_name, tables=tables)
    
    @staticmethod
    def extract_from_json(file_path: str) -> DatabaseSchema:
        """Extract schema from JSON file - supports various JSON structures"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        db_name = Path(file_path).stem
        tables = []
        
        # If JSON contains a schema definition
        if isinstance(data, dict) and 'tables' in data:
            # Direct schema format
            return DatabaseSchema(**data)
        
        # If JSON is an array of objects, infer schema
        elif isinstance(data, list) and len(data) > 0:
            sample = data[0]
            columns = []
            
            for key, value in sample.items():
                columns.append(Column(
                    name=key,
                    type=SchemaExtractor._infer_type_from_value(value),
                    primary_key=(key.lower() == 'id'),
                    nullable=True,
                    description=None
                ))
            
            tables.append(Table(
                name=db_name,
                description="Inferred from JSON array",
                columns=columns,
                foreign_keys=[]
            ))
        
        # If JSON is object with multiple arrays (each key = table)
        elif isinstance(data, dict):
            for table_name, records in data.items():
                if isinstance(records, list) and len(records) > 0:
                    sample = records[0]
                    columns = []
                    
                    for key, value in sample.items():
                        columns.append(Column(
                            name=key,
                            type=SchemaExtractor._infer_type_from_value(value),
                            primary_key=(key.lower() == 'id'),
                            nullable=True,
                            description=None
                        ))
                    
                    tables.append(Table(
                        name=table_name,
                        description=f"Inferred from JSON key: {table_name}",
                        columns=columns,
                        foreign_keys=[]
                    ))
        
        return DatabaseSchema(name=db_name, tables=tables)
    
    @staticmethod
    def extract_schema_auto(file_path: str) -> DatabaseSchema:
        """Auto-detect file type and extract schema"""
        ext = Path(file_path).suffix.lower()
        
        if ext in ['.db', '.sqlite', '.sqlite3']:
            return SchemaExtractor.extract_from_sqlite(file_path)
        elif ext in ['.xlsx', '.xls']:
            return SchemaExtractor.extract_from_excel(file_path)
        elif ext == '.csv':
            return SchemaExtractor.extract_from_csv(file_path)
        elif ext == '.sql':
            return SchemaExtractor.extract_from_sql(file_path)
        elif ext == '.json':
            return SchemaExtractor.extract_from_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def get_schema_info(file_path: str) -> Dict:
        """Get quick info about any supported file"""
        try:
            schema = SchemaExtractor.extract_schema_auto(file_path)
            total_columns = sum(len(table.columns) for table in schema.tables)
            
            ext = Path(file_path).suffix.lower()
            type_map = {
                '.db': 'SQLite', '.sqlite': 'SQLite', '.sqlite3': 'SQLite',
                '.xlsx': 'Excel', '.xls': 'Excel',
                '.csv': 'CSV',
                '.sql': 'SQL Dump',
                '.json': 'JSON'
            }
            
            return {
                "table_count": len(schema.tables),
                "total_columns": total_columns,
                "database_type": type_map.get(ext, 'Unknown')
            }
        except Exception as e:
            return {
                "error": str(e)
            }
