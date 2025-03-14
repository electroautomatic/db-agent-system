import os
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
import sys
import time
import signal

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agents.db_agent import query_agent
from app.database.models import get_db, create_tables
from app.database import queries

app = typer.Typer()
console = Console()

def check_database():
    """Check if the database has been initialized with data."""
    try:
        for db in get_db():
            movie_count = queries.get_movie_count(db)
            actor_count = queries.get_actor_count(db)
            
            if movie_count == 0 or actor_count == 0:
                console.print(Panel(
                    "[bold red]Warning: Database appears to be empty![/bold red]\n\n"
                    "Please initialize the database with:\n"
                    "[bold]docker-compose exec app python -m app.database.init_db[/bold]",
                    title="Database Check"
                ))
                return False
            else:
                console.print(Panel(
                    f"[bold green]Database is ready![/bold green]\n\n"
                    f"Found [bold]{movie_count}[/bold] movies and [bold]{actor_count}[/bold] actors.",
                    title="Database Check"
                ))
                return True
    except Exception as e:
        console.print(Panel(
            f"[bold red]Database connection error:[/bold red] {str(e)}\n\n"
            "Make sure the database is running and properly configured.",
            title="Database Error"
        ))
        return False

def display_welcome():
    """Display welcome message and instructions."""
    welcome_text = """
# TMDB Agent System

Welcome to the TMDB Agent System! This CLI allows you to chat with an AI agent about movies and actors.

## Example Questions:
* What are the top 5 highest-rated movies?
* Who starred in Inception?
* What movies were released in 2022?
* Tell me about Tom Hanks
* What popular action movies are in the database?

Type 'exit' or 'quit' to end the session.
"""
    console.print(Markdown(welcome_text))

def is_interactive():
    """Check if the script is running in an interactive terminal."""
    return sys.stdin.isatty()

def handle_sigterm(signum, frame):
    """Handle SIGTERM gracefully."""
    console.print("\n[bold yellow]Received termination signal. Shutting down...[/bold yellow]")
    sys.exit(0)

@app.command()
def main():
    """Main CLI entrypoint."""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    display_welcome()
    
    # Check database status
    db_status = check_database()
    if not db_status:
        console.print("\n[yellow]Continuing anyway, but some queries may not work as expected.[/yellow]\n")
    
    # Check if running in interactive terminal
    if not is_interactive():
        console.print(Panel(
            "[bold yellow]Non-interactive terminal detected![/bold yellow]\n\n"
            "This CLI requires an interactive terminal. To use it, run:\n"
            "[bold]docker-compose exec -it app python -m app.cli.main[/bold]\n\n"
            "For now, the application will sleep. Press Ctrl+C to exit.",
            title="Interactive Mode Required"
        ))
        try:
            # Keep the container running but don't consume CPU
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            console.print("\n[bold green]Exiting. Goodbye![/bold green]")
            sys.exit(0)
        return

    # Main interaction loop for interactive terminals
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]Ask me about movies or actors[/bold blue]")
            
            # Check for exit command
            if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                console.print("[bold green]Goodbye! Have a great day![/bold green]")
                break
            
            # Process the query
            console.print("[dim]Thinking...[/dim]")
            response = query_agent(user_input)
            
            # Display the response
            console.print(Panel(Markdown(response), title="Response"))
            
        except KeyboardInterrupt:
            console.print("\n[bold green]Goodbye! Have a great day![/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    app() 