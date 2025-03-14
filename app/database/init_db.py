import os
import sys
import time
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the parent directory to Python path to enable module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import create_tables, engine, SessionLocal, Movie, Actor
from app.api.tmdb import get_popular_movies, get_movie_details, get_movie_credits, get_actor_details

def is_interactive():
    """Check if the script is running in an interactive terminal."""
    return sys.stdin.isatty()

def init_database(force_reload=False):
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully.")
    
    db = SessionLocal()
    try:
        # Check if data already exists in the database
        movie_count = db.query(func.count(Movie.id)).scalar()
        if movie_count > 0:
            print(f"Database already contains {movie_count} movies.")
            
            if not force_reload and is_interactive():
                user_input = input("Do you want to continue and potentially add more data? (y/n): ").lower()
                if user_input != 'y':
                    print("Database initialization aborted.")
                    return
            elif not force_reload:
                print("Running in non-interactive mode. Use --force-reload flag to reload data.")
                print("Database initialization aborted.")
                return
        
        fetch_and_store_movies(db)
    finally:
        db.close()

def fetch_and_store_movies(db: Session):
    print("Fetching popular movies from TMDB API...")
    popular_movies = get_popular_movies()
    
    total_movies = len(popular_movies)
    print(f"Found {total_movies} popular movies. Fetching details and credits...")
    
    for i, movie_data in enumerate(popular_movies, 1):
        print(f"Processing movie {i}/{total_movies}: {movie_data['title']}")
        
        # Skip if movie already exists
        existing_movie = db.query(Movie).filter(Movie.tmdb_id == movie_data['id']).first()
        if existing_movie:
            print(f"Movie already exists in database: {movie_data['title']} (TMDB ID: {movie_data['id']})")
            continue
        
        # Get movie details and credits
        movie_details = get_movie_details(movie_data['id'])
        movie_credits = get_movie_credits(movie_data['id'])
        
        # Create movie record
        release_date = None
        if movie_details.get('release_date'):
            try:
                release_date = datetime.strptime(movie_details['release_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        movie = Movie(
            tmdb_id=movie_details['id'],
            title=movie_details['title'],
            overview=movie_details['overview'],
            release_date=release_date,
            vote_average=movie_details.get('vote_average'),
            vote_count=movie_details.get('vote_count'),
            poster_path=movie_details.get('poster_path'),
            backdrop_path=movie_details.get('backdrop_path'),
            popularity=movie_details.get('popularity')
        )
        
        db.add(movie)
        db.flush()  # Flush to get the movie ID
        
        # Process cast (top 10 actors)
        cast = movie_credits.get('cast', [])
        top_cast = cast[:10] if cast else []
        
        for cast_member in top_cast:
            # Check if actor already exists in the database
            actor = db.query(Actor).filter(Actor.tmdb_id == cast_member['id']).first()
            
            if not actor:
                # Get actor details
                actor_details = get_actor_details(cast_member['id'])
                
                # Parse birth and death dates
                birthday = None
                if actor_details.get('birthday'):
                    try:
                        birthday = datetime.strptime(actor_details['birthday'], '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                deathday = None
                if actor_details.get('deathday'):
                    try:
                        deathday = datetime.strptime(actor_details['deathday'], '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                # Create actor record
                actor = Actor(
                    tmdb_id=actor_details['id'],
                    name=actor_details['name'],
                    profile_path=actor_details.get('profile_path'),
                    popularity=actor_details.get('popularity'),
                    biography=actor_details.get('biography'),
                    birthday=birthday,
                    deathday=deathday,
                    place_of_birth=actor_details.get('place_of_birth')
                )
                db.add(actor)
                db.flush()  # Flush to get the actor ID
            
            # Add actor to movie
            movie.actors.append(actor)
        
        # Commit after processing each movie
        db.commit()
        
        # Sleep briefly to avoid hitting API rate limits
        time.sleep(0.5)
    
    print("Database initialization completed successfully.")

if __name__ == "__main__":
    # Check for command line arguments
    force_reload = "--force-reload" in sys.argv
    init_database(force_reload=force_reload) 