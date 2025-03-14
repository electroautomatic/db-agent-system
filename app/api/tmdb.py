import os
import requests
from typing import List, Dict, Any, Optional
import time

# TMDB API configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Ensure API key is set
if not TMDB_API_KEY:
    raise ValueError("TMDB API key is not set. Please set the TMDB_API_KEY environment variable.")

def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the TMDB API with rate limiting protection."""
    if params is None:
        params = {}
    
    # Set up headers with Bearer token
    headers = {
        "Authorization": TMDB_API_KEY if TMDB_API_KEY.startswith("Bearer") else f"Bearer {TMDB_API_KEY}",
        "Content-Type": "application/json;charset=utf-8"
    }
    
    url = f"{TMDB_BASE_URL}/{endpoint}"
    
    # Implement basic retry logic
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Rate limit hit, wait and retry
            retry_after = int(response.headers.get("Retry-After", retry_delay))
            print(f"Rate limit hit. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            # Handle other errors
            print(f"Error {response.status_code}: {response.text}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                response.raise_for_status()
    
    return {}  # Fallback empty response

def get_popular_movies(page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch popular movies from TMDB API."""
    params = {
        "page": page,
        "language": "en-US"
    }
    
    response = make_request("movie/popular", params)
    
    # Extract and return movie results
    results = response.get("results", [])
    return results[:limit]

def get_movie_details(movie_id: int) -> Dict[str, Any]:
    """Fetch detailed information for a specific movie."""
    params = {
        "language": "en-US",
        "append_to_response": "videos,images"
    }
    
    return make_request(f"movie/{movie_id}", params)

def get_movie_credits(movie_id: int) -> Dict[str, Any]:
    """Fetch cast and crew information for a specific movie."""
    return make_request(f"movie/{movie_id}/credits")

def get_actor_details(actor_id: int) -> Dict[str, Any]:
    """Fetch detailed information for a specific actor."""
    params = {
        "language": "en-US",
        "append_to_response": "movie_credits"
    }
    
    return make_request(f"person/{actor_id}", params)

def search_movies(query: str, page: int = 1) -> List[Dict[str, Any]]:
    """Search for movies by title."""
    params = {
        "query": query,
        "page": page,
        "language": "en-US"
    }
    
    response = make_request("search/movie", params)
    return response.get("results", [])

def search_people(query: str, page: int = 1) -> List[Dict[str, Any]]:
    """Search for actors/people by name."""
    params = {
        "query": query,
        "page": page,
        "language": "en-US"
    }
    
    response = make_request("search/person", params)
    return response.get("results", []) 