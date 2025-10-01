"""
SQLAgent - Natural language interface for SQL database operations using OpenAI.
"""

from typing import Dict, List, Any
import openai
import os
import json
from jinja2 import Environment, FileSystemLoader
from .database import SQLDatabase
from .tools import get_sql_tools


class SQLAgentResponseWrapper:
    """Wrapper for SQLAgentResponse that provides backward compatibility with history access."""
    
    def __init__(self, response: str, history: List[Dict[str, Any]]):
        self.response = response
        self._history = history
    
    def __str__(self) -> str:
        return self.response
    
    @property
    def history(self) -> List[Dict[str, Any]]:
        """Access the conversation history as full OpenAI messages array."""
        return self._history



class SQLAgent:
    """
    Natural language SQL agent using OpenAI function calling.
    
    Provides an async conversational interface to SQL database operations with history management.
    """
    
    def __init__(self, db: SQLDatabase, thread_id: str, model: str = "gpt-4.1-mini"):
        """
        Initialize SQLAgent with database connection and conversation settings.
        
        Args:
            db: SQLDatabase instance for database operations
            thread_id: Unique identifier for conversation thread
            model: Model provider string (e.g., "openai/gpt-4.1-mini")
        """
        self.db = db
        self.thread_id = thread_id
        self.model = model

        # Initialize Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Initialize AsyncOpenAI client
        self.client = openai.AsyncOpenAI()
        
        # Conversation history storage (in-memory for now)
        if not hasattr(SQLAgent, '_conversations'):
            SQLAgent._conversations = {}
        
        if thread_id not in SQLAgent._conversations:
            SQLAgent._conversations[thread_id] = []
    
    
    async def run(self, user_query: str, max_iterations: int = 10) -> SQLAgentResponseWrapper:
        """
        Process a natural language query using iterative tool usage.
        
        The agent will use SQL tools iteratively until it has enough information
        to provide a final response via SQLAgentResponse.
        
        Args:
            user_query: Natural language query from the user
            max_iterations: Maximum number of tool iterations before stopping
            
        Returns:
            SQLAgentResponse object with the final response
        """
        # Load existing conversation history
        if self.thread_id not in SQLAgent._conversations:
            SQLAgent._conversations[self.thread_id] = []
        
        messages = SQLAgent._conversations[self.thread_id].copy()
        
        # Add system prompt if this is a new conversation
        if not messages:
            system_template = self.jinja_env.get_template('system_prompt.j2')
            system_content = system_template.render()
            messages.append({
                "role": "system", 
                "content": system_content
            })
        
        # Add current user query to messages
        user_message = {
            "role": "user",
            "content": user_query
        }
        messages.append(user_message)
        
        # Get SQL tools from tools module
        tools = get_sql_tools()
        
        
        # Iterative tool usage loop
        iteration = 0
        while iteration < max_iterations:
            try:
                # Get response with tool calls from OpenAI
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                
                # If no tool calls, check if it's a final response
                if not assistant_message.tool_calls:
                    if assistant_message.content:
                        # Add final response to messages
                        final_message = {
                            "role": "assistant",
                            "content": assistant_message.content
                        }
                        messages.append(final_message)
                        
                        # Persist complete conversation
                        SQLAgent._conversations[self.thread_id] = messages
                        return SQLAgentResponseWrapper(assistant_message.content, messages.copy())
                    else:
                        # Model didn't provide content or tool calls
                        continue
                
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant", 
                    "tool_calls": [tool_call.model_dump() for tool_call in assistant_message.tool_calls]
                })
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the appropriate database operation
                    if function_name == "sql_db_list_tables":
                        result = self.db.sql_db_list_tables("")
                    elif function_name == "sql_db_schema":
                        result = self.db.sql_db_schema(function_args.get("tables", ""))
                    elif function_name == "sql_db_query_checker":
                        result = self.db.sql_db_query_checker(function_args.get("query", ""))
                    elif function_name == "sql_db_query":
                        result = self.db.sql_db_query(function_args.get("query", ""))
                    else:
                        result = f"Unknown function: {function_name}"
                    
                    # Add tool result message
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                
                iteration += 1
                
            except Exception as e:
                # If there's an error, return it as the final response
                error_message = f"I encountered an error while processing your query: {str(e)}"
                
                error_response = {
                    "role": "assistant", 
                    "content": error_message
                }
                messages.append(error_response)
                
                # Persist complete conversation  
                SQLAgent._conversations[self.thread_id] = messages
                return SQLAgentResponseWrapper(error_message, messages.copy())
        
        # If max iterations reached without final response
        timeout_message = "I've reached the maximum number of steps while processing your query. Please try rephrasing your question or breaking it into smaller parts."
        
        timeout_response = {
            "role": "assistant",
            "content": timeout_message
        }
        messages.append(timeout_response)
        
        # Persist complete conversation
        SQLAgent._conversations[self.thread_id] = messages
        return SQLAgentResponseWrapper(timeout_message, messages.copy())