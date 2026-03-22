from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Movie
from schemas import MovieOut
from services.tmdb import search_movies, get_movie_details, get_popular_movies, parse_tmdb_movie

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/search")
async def search(query: str, db: Session = Depends(get_db)):
    """Search for films (first check the local database; if not found, call upon TMDB)"""
    # Check locally first
    local = db.query(Movie).filter(Movie.title.ilike(f"%{query}%")).all()
    if local:
        return {"source": "local", "results": [m for m in local if m.title]}

    # If not found locally, call TMDB
    results = await search_movies(query)
    if not results:
        raise HTTPException(status_code=404, detail="No movies found")

    # Cached to the local database
    saved = []
    for item in results[:5]:  # Only the first five entries are retained
        existing = db.query(Movie).filter(Movie.tmdb_id == item["id"]).first()
        if not existing:
            movie_data = parse_tmdb_movie(item)
            movie = Movie(**movie_data)
            db.add(movie)
            db.commit()
            db.refresh(movie)
            saved.append(movie)
        else:
            saved.append(existing)

    return {"source": "tmdb", "results": saved}


@router.get("/popular")
async def popular(db: Session = Depends(get_db)):
    """Access popular films"""
    results = await get_popular_movies()
    if not results:
        raise HTTPException(status_code=404, detail="No popular movies found")

    saved = []
    for item in results[:10]:
        existing = db.query(Movie).filter(Movie.tmdb_id == item["id"]).first()
        if not existing:
            movie_data = parse_tmdb_movie(item)
            movie = Movie(**movie_data)
            db.add(movie)
            db.commit()
            db.refresh(movie)
            saved.append(movie)
        else:
            saved.append(existing)

    return {"results": [m for m in saved if m.title]}


@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single film (search locally first; if unavailable, fetch from TMDB)"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        return movie

    # Attempt to retrieve from TMDB
    try:
        data = await get_movie_details(movie_id)
        movie_data = parse_tmdb_movie(data)
        movie = Movie(**movie_data)
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie
    except Exception:
        raise HTTPException(status_code=404, detail="Movie not found")