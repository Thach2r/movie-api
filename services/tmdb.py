import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def search_movies(query: str):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "en-US",
        "page": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])

async def get_movie_details(tmdb_id: int):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_popular_movies():
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])

def parse_tmdb_movie(data: dict) -> dict:
    genres = data.get("genres", [])
    genre_str = ", ".join([g["name"] for g in genres]) if genres else data.get("genre_ids", "")
    if isinstance(genre_str, list):
        genre_str = ", ".join(str(g) for g in genre_str)

    return {
        "tmdb_id": data.get("id"),
        "title": data.get("title"),
        "overview": data.get("overview"),
        "release_date": data.get("release_date"),
        "genre": genre_str,
        "rating": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "revenue": data.get("revenue", 0),
        "poster_path": data.get("poster_path")
    }