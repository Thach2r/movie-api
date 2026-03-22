from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Movie, BoxOfficeMovie

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/genre-ratings")
def genre_ratings(db: Session = Depends(get_db)):
    """Get average rating by genre"""
    movies = db.query(BoxOfficeMovie).filter(BoxOfficeMovie.genre != None, BoxOfficeMovie.score != None).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movie data found")

    genre_data = {}
    for movie in movies:
        genres = [g.strip() for g in movie.genre.split(",")]
        for genre in genres:
            if genre not in genre_data:
                genre_data[genre] = {"total_rating": 0, "count": 0}
            genre_data[genre]["total_rating"] += movie.score
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
    movies = db.query(BoxOfficeMovie).filter(BoxOfficeMovie.score != None).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No rating data found")

    distribution = {
        "1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0,
        "5-6": 0, "6-7": 0, "7-8": 0, "8-9": 0, "9-10": 0
    }
    for movie in movies:
        rating = movie.score
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
    movies = db.query(BoxOfficeMovie).filter(
        BoxOfficeMovie.genre.ilike(f"%{genre}%"),
        BoxOfficeMovie.score != None
    ).order_by(BoxOfficeMovie.score.desc()).limit(10).all()

    if not movies:
        raise HTTPException(status_code=404, detail=f"No movies found for genre: {genre}")

    return {
        "genre": genre,
        "recommendations": [
            {
                "title": m.name,
                "year": m.year,
                "rating": m.score,
                "director": m.director,
                "genre": m.genre
            }
            for m in movies
        ]
    }


@router.get("/top-box-office")
def top_box_office(
    decade: int = None,
    n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get top N movies by box office gross, optionally filtered by decade.

    - **decade**: Starting year of the decade, e.g. `1990` for the 1990s (optional)
    - **n**: Number of results to return, default 10, max 50
    """
    if n < 1 or n > 50:
        raise HTTPException(status_code=400, detail="n must be between 1 and 50")

    query = db.query(BoxOfficeMovie).filter(
        BoxOfficeMovie.gross != None,
        BoxOfficeMovie.gross > 0,
        BoxOfficeMovie.year != None
    )

    if decade is not None:
        if decade % 10 != 0:
            raise HTTPException(status_code=400, detail="decade must be a multiple of 10, e.g. 1990")
        query = query.filter(
            BoxOfficeMovie.year >= decade,
            BoxOfficeMovie.year < decade + 10
        )

    movies = query.order_by(BoxOfficeMovie.gross.desc()).limit(n).all()

    if not movies:
        detail = f"No box office data found for the {decade}s" if decade else "No box office data found"
        raise HTTPException(status_code=404, detail=detail)

    results = [
        {
            "rank": idx + 1,
            "title": m.name,
            "year": m.year,
            "gross": round(m.gross),
            "genre": m.genre,
            "director": m.director,
        }
        for idx, m in enumerate(movies)
    ]

    return {
        "decade": f"{decade}s" if decade else "all time",
        "top_n": n,
        "count": len(results),
        "results": results
    }