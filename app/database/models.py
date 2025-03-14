from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tmdb_user:tmdb_password@localhost:5432/tmdb_database")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for Movie-Actor many-to-many relationship
movie_actor = Table(
    'movie_actor',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('actor_id', Integer, ForeignKey('actors.id'), primary_key=True)
)

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True)
    title = Column(String(255), index=True)
    overview = Column(Text)
    release_date = Column(Date, nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    poster_path = Column(String(255), nullable=True)
    backdrop_path = Column(String(255), nullable=True)
    popularity = Column(Float, nullable=True)
    
    # Relationships
    actors = relationship("Actor", secondary=movie_actor, back_populates="movies")

class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True)
    name = Column(String(255), index=True)
    profile_path = Column(String(255), nullable=True)
    popularity = Column(Float, nullable=True)
    biography = Column(Text, nullable=True)
    birthday = Column(Date, nullable=True)
    deathday = Column(Date, nullable=True)
    place_of_birth = Column(String(255), nullable=True)
    
    # Relationships
    movies = relationship("Movie", secondary=movie_actor, back_populates="actors")

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine) 