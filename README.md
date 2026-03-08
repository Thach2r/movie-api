# CineMetrics API

A movie analytics and review API powered by TMDB and Kaggle datasets.

## Tech Stack

- **Framework**: Python FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **External API**: TMDB (The Movie Database)
- **Dataset**: Kaggle – Movie Industry Dataset (1986–2016)

## Features

- Search and browse movies via TMDB with local caching
- Full CRUD for movie reviews and tags
- API key authentication for all write operations
- Analytics: box office trends, genre ratings, rating distribution, top N per decade, recommendations

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Thach2r/movie-api.git
cd movie-api
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy httpx python-dotenv pytest
```

### 4. Configure environment variables

Set the following environment variables before starting the server:

```bash
export TMDB_API_KEY="your_tmdb_api_key_here"
export API_KEY="your_api_key_here"
```

| Variable | Required | Description |
|----------|----------|-------------|
| `TMDB_API_KEY` | Yes | Your TMDB API key from themoviedb.org |
| `API_KEY` | Yes | Secret key for authenticating write operations |

### 5. Import Kaggle dataset

```bash
python import_kaggle.py
```

This imports 7,479 movies from the bundled `movies.csv` (1986–2016 box office data).

### 6. Run the server

```bash
uvicorn main:app --reload
```

- Base URL: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

### 7. Run tests

```bash
pytest test_api.py -v
```

Expected output: **14 passed**.

---

## Authentication

Read endpoints (`GET`) are **publicly accessible** with no authentication required.

Write endpoints (`POST`, `PUT`, `DELETE`) require an `X-API-Key` header:

```bash
curl -X POST http://127.0.0.1:8000/reviews/ \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1, "author": "Alice", "content": "Great film!", "score": 8.5}'
```

Missing or invalid keys return `401 Unauthorized` or `403 Forbidden` respectively.

---

## API Endpoints

### Movies

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/movies/search?query=` | No | Search movies (local DB first, then TMDB) |
| GET | `/movies/popular` | No | Get popular movies from TMDB |
| GET | `/movies/{id}` | No | Get movie details |

### Reviews (CRUD)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/reviews/` | **Yes** | Create a review |
| GET | `/reviews/` | No | Get all reviews |
| GET | `/reviews/{id}` | No | Get a single review |
| GET | `/reviews/movie/{movie_id}` | No | Get all reviews for a movie |
| PUT | `/reviews/{id}` | **Yes** | Update a review |
| DELETE | `/reviews/{id}` | **Yes** | Delete a review |

### Tags (CRUD)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/tags/` | **Yes** | Create a tag |
| GET | `/tags/` | No | Get all tags |
| GET | `/tags/{id}` | No | Get a single tag |
| PUT | `/tags/{id}` | **Yes** | Update a tag |
| DELETE | `/tags/{id}` | **Yes** | Delete a tag |
| POST | `/movies/{id}/tags` | **Yes** | Add a tag to a movie |
| GET | `/movies/{id}/tags` | No | Get all tags for a movie |
| DELETE | `/movies/{id}/tags/{tag_id}` | **Yes** | Remove a tag from a movie |

### Analytics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/analytics/box-office-trends` | No | Box office trends by decade (Kaggle) |
| GET | `/analytics/genre-ratings` | No | Average rating by genre |
| GET | `/analytics/rating-distribution` | No | Rating distribution across all movies |
| GET | `/analytics/recommend?genre=` | No | Top movie recommendations by genre |
| GET | `/analytics/top-box-office?decade=&n=` | No | Top N movies by gross, filtered by decade |

**Example – Top 5 films of the 1990s:**
```
GET /analytics/top-box-office?decade=1990&n=5
```

---

## Data Sources

- **TMDB API**: https://www.themoviedb.org/documentation/api
- **Kaggle Dataset**: Movie Industry Dataset by Daniel Grijalva (CC0 Public Domain License)

---

## API Documentation

Full API documentation (all endpoints, parameters, example responses) is available as a PDF:

**[CineMetrics API - Swagger UI.pdf](./CineMetrics%20API%20-%20Swagger%20UI.pdf)**

---

## Technical Report
[Technical Report (PDF)](./technical_report.pdf)
