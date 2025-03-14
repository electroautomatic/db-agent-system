import os
from typing import List, Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
import json

from langchain.agents import AgentExecutor  
from langchain_community.agent_toolkits.sql.base import create_sql_agent  
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.database.models import get_db
from app.database import queries

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# Create LLM using OpenAI
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")

# Database URL for connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tmdb_user:tmdb_password@postgres:5432/tmdb_database")

# Create SQL database connection for LangChain
db = SQLDatabase.from_uri(DATABASE_URL)

# Create SQL database toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create custom database tools using our query functions
def create_tool_from_query_fn(fn: Callable, name: str, description: str) -> Tool:
    """Helper function to convert a database query function into a LangChain tool."""
    def tool_fn(*args, **kwargs):
        try:
            # Get a DB session
            for db_session in get_db():
                # Execute the query function with the session and args
                result = fn(db_session, *args, **kwargs)
                
                # Handle different return types
                if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                    # Convert list of ORM objects to list of dicts
                    return json.dumps([{
                        column.key: getattr(item, column.key)
                        for column in item.__table__.columns
                    } for item in result], default=str)
                elif hasattr(result, '__table__'):
                    # Single ORM object
                    return json.dumps({
                        column.key: getattr(result, column.key)
                        for column in result.__table__.columns
                    }, default=str)
                else:
                    # Simple value or None
                    return json.dumps(result, default=str)
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    return Tool(
        name=name,
        func=tool_fn,
        description=description
    )

# Custom tools derived from our query functions
tools = [
    create_tool_from_query_fn(
        queries.search_movies_by_title,
        "search_movies_by_title",
        "Search for movies by title. Args: title (str), limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.search_actors_by_name,
        "search_actors_by_name",
        "Search for actors by name. Args: name (str), limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.get_top_rated_movies,
        "get_top_rated_movies",
        "Get top-rated movies. Args: limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.get_popular_movies,
        "get_popular_movies",
        "Get popular movies. Args: limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.get_movies_by_year,
        "get_movies_by_year",
        "Get movies released in a specific year. Args: year (int), limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.get_actors_in_movie,
        "get_actors_in_movie",
        "Get actors who appeared in a specific movie. Args: movie_id (int), limit (int, optional)"
    ),
    create_tool_from_query_fn(
        queries.get_movies_by_actor,
        "get_movies_by_actor",
        "Get movies a specific actor appeared in. Args: actor_id (int), limit (int, optional)"
    ),
]

# Create SQL agent
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False,
    agent_type="openai-tools",
    handle_parsing_errors=True,
)

# System message template for the agent
template = """You are a helpful assistant that answers questions about movies and actors.
You have access to a movie database with information from TMDB.
If you need to query specific data, you can use the SQL agent. For common queries, use the provided tools.
Always format your responses in a clear, readable manner. If returning movie or actor information, present it in a friendly format."""

# Create agent executor with all tools
all_tools = tools + sql_agent.tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=sql_agent.agent,
    tools=all_tools,
    verbose=False,
    handle_parsing_errors=True,
    return_intermediate_steps=False,
    max_iterations=10,
)

def query_agent(query: str) -> str:
    """
    Query the agent with a natural language question.
    
    Args:
        query: The natural language query string
        
    Returns:
        The agent's response as a string
    """
    try:
        # Use invoke instead of run, and extract the output from the response
        response = agent_executor.invoke({"input": query})
        # Extract the output text from the response
        if isinstance(response, dict) and "output" in response:
            return response["output"]
        else:
            return str(response)
    except Exception as e:
        return f"An error occurred: {str(e)}" 