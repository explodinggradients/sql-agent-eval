"""
SQL Agent Tools - OpenAI function calling tool definitions for SQL database operations.
"""

from typing import List, Dict, Any


def get_sql_tools() -> List[Dict[str, Any]]:
    """
    Get all SQL database tools for OpenAI function calling.
    
    Returns:
        List of OpenAI function calling tool definitions
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "sql_db_list_tables",
                "description": "List all available tables in the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "empty_input": {"type": "string", "description": "Empty string input (not used)"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "sql_db_schema",
                "description": "Get table structure and sample data for specified tables",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tables": {"type": "string", "description": "Comma-separated list of table names"}
                    },
                    "required": ["tables"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "sql_db_query_checker", 
                "description": "Validate SQL queries before execution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to validate"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "sql_db_query",
                "description": "Execute SQL queries against the database", 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Valid SQL query to execute"}
                    },
                    "required": ["query"]
                }
            }
        },
    ]