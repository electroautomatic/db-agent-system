# TMDB Agent System

A command-line agent system that interacts with a local Postgres database containing movie data from TMDB API.

![L2 diagram](./docs/svg/TMDB%20Agent%20System%20-%20Container%20Diagram%20(L2).svg)
## Features

- Automated setup of a local Postgres database with Docker
- Data loading from TMDB API into structured tables (movies, actors)
- Interactive CLI with AI agents that can query the database
- LangChain integration with OpenAI API for natural language processing

## Prerequisites

- Docker and Docker Compose
- TMDB API Key (get one from [themoviedb.org](https://www.themoviedb.org/documentation/api))
- OpenAI API Key

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd tmdb-agent-system
   ```

2. Create a `.env` file in the project root with your API keys:
   ```
   # For TMDB API v4 (using Bearer token)
   TMDB_API_KEY=Bearer your_tmdb_api_access_token
   
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key
   ```
   Note: For TMDB API, make sure to include the `Bearer ` prefix if you're using the v4 API authentication method. You can obtain your access token from the TMDB API settings page.

3. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

4. Access the database management interface:
   Adminer is available at [http://localhost:8080](http://localhost:8080)
   - System: PostgreSQL
   - Server: postgres
   - Username: tmdb_user
   - Password: tmdb_password
   - Database: tmdb_database

5. Initialize the database and fetch TMDB data:
   ```
   docker-compose exec app python -m app.database.init_db
   ```
   
   If you need to reload data into an existing database, use the force-reload flag:
   ```
   docker-compose exec app python -m app.database.init_db --force-reload
   ```

6. Run the CLI interface in interactive mode:
   ```
   docker-compose exec -it app python -m app.cli.main
   ```

## Usage

After starting the CLI, you can interact with the agent by typing natural language queries, such as:

- "Find write the top 3 highest-rated movies."
- "Who played in the movie Gladiator 2?"
- "What is most popular actor?"

The agent will translate your queries into database operations and return the results.

## Project Structure

```
app/
├── api/              # TMDB API interaction
├── agents/           # LangChain agent definitions
├── database/         # Database models and operations
├── cli/              # Command-line interface
```

