from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Review, Movie
from schemas import ReviewCreate, ReviewUpdate, ReviewOut
from typing import List

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewOut)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review"""
    movie = db.query(Movie).filter(Movie.id == review.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    new_review = Review(**review.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.get("/", response_model=List[ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    """Get all reviews"""
    return db.query(Review).all()


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get a single review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/movie/{movie_id}", response_model=List[ReviewOut])
def get_reviews_by_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific movie"""
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this movie")
    return reviews


@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, review_data: ReviewUpdate, db: Session = Depends(get_db)):
    """Update an existing review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = review_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": f"Review {review_id} deleted successfully"}