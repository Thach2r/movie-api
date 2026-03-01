from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Movie, Review

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/genre-ratings")
def genre_ratings(db: Session = Depends(get_db)):
    """Get average rating by genre"""
    movies = db.query(Movie).filter(Movie.genre != None, Movie.rating != None).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movie data found")

    genre_data = {}
    for movie in movies:
        genres = [g.strip() for g in movie.genre.split(",")]
        for genre in genres:
            if genre not in genre_data:
                genre_data[genre] = {"total_rating": 0, "count": 0}
            genre_data[genre]["total_rating"] += movie.rating
            genre_data[genre]["count"] += 1

    results = [
        {
            "genre": genre,
            "average_rating": round(data["total_rating"] / data["count"], 2),
            "movie_count": data["count"]
        }
        for genre, data in genre_data.items()
    ]

    results.sort(key=lambda x: x["average_rating"], reverse=True)
    return {"genre_ratings": results}


@router.get("/box-office-trends")
def box_office_trends(db: Session = Depends(get_db)):
    """Get box office trends by decade using Kaggle dataset"""
    from models import BoxOfficeMovie

    movies = db.query(BoxOfficeMovie).filter(
        BoxOfficeMovie.year != None,
        BoxOfficeMovie.gross != None,
        BoxOfficeMovie.gross > 0
    ).all()

    if not movies:
        raise HTTPException(status_code=404, detail="No box office data found")

    decade_data = {}
    for movie in movies:
        decade = f"{(movie.year // 10) * 10}s"
        if decade not in decade_data:
            decade_data[decade] = {"total_gross": 0, "count": 0, "top_movie": None, "top_gross": 0}
        decade_data[decade]["total_gross"] += movie.gross
        decade_data[decade]["count"] += 1
        if movie.gross > decade_data[decade]["top_gross"]:
            decade_data[decade]["top_gross"] = movie.gross
            decade_data[decade]["top_movie"] = movie.name

    results = [
        {
            "decade": decade,
            "average_gross": round(data["total_gross"] / data["count"]),
            "total_gross": round(data["total_gross"]),
            "movie_count": data["count"],
            "top_movie": data["top_movie"],
            "top_movie_gross": round(data["top_gross"])
        }
        for decade, data in decade_data.items()
    ]

    results.sort(key=lambda x: x["decade"])
    return {"box_office_trends": results}


@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    """Get distribution of movie ratings"""
    movies = db.query(Movie).filter(Movie.rating != None).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No rating data found")

    distribution = {
        "1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0,
        "5-6": 0, "6-7": 0, "7-8": 0, "8-9": 0, "9-10": 0
    }

    for movie in movies:
        rating = movie.rating
        if rating < 2: distribution["1-2"] += 1
        elif rating < 3: distribution["2-3"] += 1
        elif rating < 4: distribution["3-4"] += 1
        elif rating < 5: distribution["4-5"] += 1
        elif rating < 6: distribution["5-6"] += 1
        elif rating < 7: distribution["6-7"] += 1
        elif rating < 8: distribution["7-8"] += 1
        elif rating < 9: distribution["8-9"] += 1
        else: distribution["9-10"] += 1

    return {"total_movies": len(movies), "rating_distribution": distribution}


@router.get("/recommend")
def recommend(genre: str, db: Session = Depends(get_db)):
    """Recommend top movies by genre"""
    movies = db.query(Movie).filter(
        Movie.genre.ilike(f"%{genre}%"),
        Movie.rating != None
    ).order_by(Movie.rating.desc()).limit(10).all()

    if not movies:
        raise HTTPException(status_code=404, detail=f"No movies found for genre: {genre}")

    return {
        "genre": genre,
        "recommendations": [
            {
                "id": m.id,
                "title": m.title,
                "rating": m.rating,
                "release_date": m.release_date,
                "overview": m.overview
            }
            for m in movies
        ]
    }