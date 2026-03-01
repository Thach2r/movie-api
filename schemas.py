from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Movie
class MovieBase(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    vote_count: Optional[int] = None
    revenue: Optional[int] = None
    poster_path: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class MovieOut(MovieBase):
    id: int

    class Config:
        from_attributes = True


# Review
class ReviewCreate(BaseModel):
    movie_id: int
    author: str
    content: str
    score: float = Field(ge=0, le=10)

class ReviewUpdate(BaseModel):
    author: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = Field(default=None, ge=0, le=10)

class ReviewOut(BaseModel):
    id: int
    movie_id: int
    author: str
    content: str
    score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tag 
class TagCreate(BaseModel):
    name: str

class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# MovieTag 
class MovieTagCreate(BaseModel):
    tag_id: int

class MovieTagOut(BaseModel):
    id: int
    movie_id: int
    tag_id: int

    class Config:
        from_attributes = True