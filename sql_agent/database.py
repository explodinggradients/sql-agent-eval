import sqlparse
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Any, List
import logging


class SQLDatabase:
    def __init__(self, database_uri: str):
        """
        Initialize SQLDatabase with a database connection URI.
        
        Args:
            database_uri: Database connection string (e.g., "sqlite:///database.db")
        """
        self.database_uri = database_uri
        self.engine = create_engine(database_uri)
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test the database connection on initialization."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def sql_db_query(self, query: str) -> str:
        """
        Execute a SQL query and return the results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            String representation of query results or error message
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Handle different types of queries
                if result.returns_rows:
                    rows = result.fetchall()
                    if not rows:
                        return "No rows returned."
                    
                    # Get column names
                    columns = list(result.keys())
                    
                    # Format results as a table
                    formatted_result = []
                    formatted_result.append(" | ".join(columns))
                    formatted_result.append("-" * len(formatted_result[0]))
                    
                    for row in rows:
                        formatted_result.append(" | ".join(str(value) if value is not None else "NULL" for value in row))
                    
                    return "\n".join(formatted_result)
                else:
                    # For INSERT, UPDATE, DELETE operations
                    rowcount = result.rowcount
                    return f"Query executed successfully. {rowcount} row(s) affected."
                    
        except SQLAlchemyError as e:
            return f"Error executing query: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def sql_db_list_tables(self, empty_input: str = "") -> str:
        """
        List all tables in the database.
        
        Args:
            empty_input: Unused parameter (for compatibility with description)
            
        Returns:
            Comma-separated list of table names
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                return "No tables found in the database."
            
            return ", ".join(tables)
            
        except SQLAlchemyError as e:
            return f"Error retrieving table list: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def sql_db_schema(self, tables: str) -> str:
        """
        Get schema information and sample rows for specified tables.
        
        Args:
            tables: Comma-separated list of table names
            
        Returns:
            Schema information and sample rows for each table
        """
        try:
            table_list = [table.strip() for table in tables.split(",") if table.strip()]
            
            if not table_list:
                return "No tables specified."
            
            inspector = inspect(self.engine)
            all_tables = inspector.get_table_names()
            
            result_parts = []
            
            for table_name in table_list:
                if table_name not in all_tables:
                    result_parts.append(f"Table '{table_name}' does not exist.")
                    continue
                
                # Get column information
                columns = inspector.get_columns(table_name)
                
                schema_info = [f"\nTable: {table_name}"]
                schema_info.append("Columns:")
                
                for column in columns:
                    col_type = str(column['type'])
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    default = f" DEFAULT {column['default']}" if column['default'] is not None else ""
                    schema_info.append(f"  - {column['name']}: {col_type} {nullable}{default}")
                
                # Get sample rows
                try:
                    with self.engine.connect() as conn:
                        sample_result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                        sample_rows = sample_result.fetchall()
                        
                        if sample_rows:
                            schema_info.append("\nSample rows:")
                            column_names = [col['name'] for col in columns]
                            schema_info.append(" | ".join(column_names))
                            schema_info.append("-" * len(schema_info[-1]))
                            
                            for row in sample_rows:
                                schema_info.append(" | ".join(str(value) if value is not None else "NULL" for value in row))
                        else:
                            schema_info.append("\nNo sample rows available (table is empty).")
                
                except SQLAlchemyError as e:
                    schema_info.append(f"\nError retrieving sample rows: {str(e)}")
                
                result_parts.append("\n".join(schema_info))
            
            return "\n\n".join(result_parts)
            
        except SQLAlchemyError as e:
            return f"Error retrieving schema information: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def sql_db_query_checker(self, query: str) -> str:
        """
        Validate SQL query syntax.
        
        Args:
            query: SQL query to validate
            
        Returns:
            Syntax validation results
        """
        try:
            if not query or not query.strip():
                return "Error: Empty query provided."
            
            # Parse the SQL query using sqlparse
            parsed = sqlparse.parse(query.strip())
            
            if not parsed:
                return "Error: Unable to parse the SQL query."
            
            statement = parsed[0]
            
            # Check if it's a valid SQL statement
            if statement.get_type() == 'UNKNOWN':
                return "Error: Unable to determine query type - invalid SQL syntax."
            
            return "✓ Query syntax is valid."
            
        except Exception as e:
            return f"Error validating query syntax: {str(e)}"