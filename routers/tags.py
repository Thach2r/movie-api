from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Tag, MovieTag, Movie
from schemas import TagCreate, TagOut, MovieTagCreate, MovieTagOut
from typing import List

router = APIRouter(tags=["Tags"])


@router.post("/tags/", response_model=TagOut)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag"""
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/tags/", response_model=List[TagOut])
def get_all_tags(db: Session = Depends(get_db)):
    """Get all tags"""
    return db.query(Tag).all()


@router.get("/tags/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a single tag by ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, tag_data: TagCreate, db: Session = Depends(get_db)):
    """Update an existing tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.name = tag_data.name
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()
    return {"message": f"Tag {tag_id} deleted successfully"}


@router.post("/movies/{movie_id}/tags", response_model=MovieTagOut)
def add_tag_to_movie(movie_id: int, tag_data: MovieTagCreate, db: Session = Depends(get_db)):
    """Add a tag to a movie"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    tag = db.query(Tag).filter(Tag.id == tag_data.tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    existing = db.query(MovieTag).filter(
        MovieTag.movie_id == movie_id,
        MovieTag.tag_id == tag_data.tag_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already added to this movie")

    movie_tag = MovieTag(movie_id=movie_id, tag_id=tag_data.tag_id)
    db.add(movie_tag)
    db.commit()
    db.refresh(movie_tag)
    return movie_tag


@router.get("/movies/{movie_id}/tags")
def get_tags_for_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get all tags for a specific movie"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie_tags = db.query(MovieTag).filter(MovieTag.movie_id == movie_id).all()
    return {"movie_id": movie_id, "tags": [mt.tag for mt in movie_tags]}


@router.delete("/movies/{movie_id}/tags/{tag_id}")
def remove_tag_from_movie(movie_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Remove a tag from a movie"""
    movie_tag = db.query(MovieTag).filter(
        MovieTag.movie_id == movie_id,
        MovieTag.tag_id == tag_id
    ).first()
    if not movie_tag:
        raise HTTPException(status_code=404, detail="Tag not found on this movie")

    db.delete(movie_tag)
    db.commit()
    return {"message": f"Tag {tag_id} removed from movie {movie_id}"}