from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    overview = Column(Text)
    release_date = Column(String)
    genre = Column(String)
    rating = Column(Float)
    vote_count = Column(Integer)
    revenue = Column(Integer)
    poster_path = Column(String)

    reviews = relationship("Review", back_populates="movie")
    movie_tags = relationship("MovieTag", back_populates="movie")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    author = Column(String)
    content = Column(Text)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    movie = relationship("Movie", back_populates="reviews")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    movie_tags = relationship("MovieTag", back_populates="tag")


class MovieTag(Base):
    __tablename__ = "movie_tags"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    movie = relationship("Movie", back_populates="movie_tags")
    tag = relationship("Tag", back_populates="movie_tags")

class BoxOfficeMovie(Base):
    __tablename__ = "boxoffice_movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    genre = Column(String)
    year = Column(Integer, index=True)
    score = Column(Float)
    votes = Column(Float)
    director = Column(String)
    star = Column(String)
    country = Column(String)
    budget = Column(Float)
    gross = Column(Float)
    company = Column(String)
    runtime = Column(Float)