from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime

from app.database.models import Movie, Actor

def get_movie_by_id(db: Session, movie_id: int) -> Optional[Movie]:
    """Get a movie by its ID."""
    return db.query(Movie).filter(Movie.id == movie_id).first()

def get_movie_by_tmdb_id(db: Session, tmdb_id: int) -> Optional[Movie]:
    """Get a movie by its TMDB ID."""
    return db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()

def get_actor_by_id(db: Session, actor_id: int) -> Optional[Actor]:
    """Get an actor by their ID."""
    return db.query(Actor).filter(Actor.id == actor_id).first()

def get_actor_by_tmdb_id(db: Session, tmdb_id: int) -> Optional[Actor]:
    """Get an actor by their TMDB ID."""
    return db.query(Actor).filter(Actor.tmdb_id == tmdb_id).first()

def search_movies_by_title(db: Session, title: str, limit: int = 10) -> List[Movie]:
    """Search for movies by title."""
    return db.query(Movie).filter(Movie.title.ilike(f"%{title}%")).limit(limit).all()

def search_actors_by_name(db: Session, name: str, limit: int = 10) -> List[Actor]:
    """Search for actors by name."""
    return db.query(Actor).filter(Actor.name.ilike(f"%{name}%")).limit(limit).all()

def get_top_rated_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get top-rated movies based on vote average."""
    return db.query(Movie).order_by(desc(Movie.vote_average)).limit(limit).all()

def get_popular_movies(db: Session, limit: int = 10) -> List[Movie]:
    """Get popular movies based on popularity score."""
    return db.query(Movie).order_by(desc(Movie.popularity)).limit(limit).all()

def get_movies_by_year(db: Session, year: int, limit: int = 10) -> List[Movie]:
    """Get movies released in a specific year."""
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    return db.query(Movie).filter(
        Movie.release_date >= start_date,
        Movie.release_date <= end_date
    ).limit(limit).all()

def get_actors_in_movie(db: Session, movie_id: int, limit: int = 10) -> List[Actor]:
    """Get actors who appeared in a specific movie."""
    movie = get_movie_by_id(db, movie_id)
    if movie:
        return movie.actors[:limit]
    return []

def get_movies_by_actor(db: Session, actor_id: int, limit: int = 10) -> List[Movie]:
    """Get movies that a specific actor appeared in."""
    actor = get_actor_by_id(db, actor_id)
    if actor:
        return actor.movies[:limit]
    return []

def get_all_movies(db: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
    """Get all movies with pagination."""
    return db.query(Movie).offset(skip).limit(limit).all()

def get_all_actors(db: Session, skip: int = 0, limit: int = 100) -> List[Actor]:
    """Get all actors with pagination."""
    return db.query(Actor).offset(skip).limit(limit).all()

def get_movie_count(db: Session) -> int:
    """Get the total number of movies in the database."""
    return db.query(func.count(Movie.id)).scalar()

def get_actor_count(db: Session) -> int:
    """Get the total number of actors in the database."""
    return db.query(func.count(Actor.id)).scalar() 