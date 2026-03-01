# CineMetrics API

A movie analytics and review API powered by TMDB and Kaggle datasets.

## Tech Stack

- **Framework**: Python FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **External API**: TMDB (The Movie Database)
- **Dataset**: Kaggle - Movie Industry Dataset (1986-2016)

## Features

- Search and browse movies via TMDB
- Full CRUD for movie reviews and tags
- Analytics: box office trends, genre ratings, rating distribution, recommendations

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
pip install fastapi uvicorn sqlalchemy httpx python-dotenv
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```
TMDB_API_KEY=your_tmdb_api_key_here
```

### 5. Import Kaggle dataset
```bash
python import_kaggle.py
```

### 6. Run the server
```bash
uvicorn main:app --reload
```

### 7. Access the API
- Base URL: http://127.0.0.1:8000
- Swagger Docs: http://127.0.0.1:8000/docs

## API Endpoints

### Movies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /movies/search?query= | Search movies via TMDB |
| GET | /movies/popular | Get popular movies |
| GET | /movies/{id} | Get movie details |

### Reviews (CRUD)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /reviews/ | Create a review |
| GET | /reviews/ | Get all reviews |
| GET | /reviews/{id} | Get a review |
| PUT | /reviews/{id} | Update a review |
| DELETE | /reviews/{id} | Delete a review |

### Tags (CRUD)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /tags/ | Create a tag |
| GET | /tags/ | Get all tags |
| PUT | /tags/{id} | Update a tag |
| DELETE | /tags/{id} | Delete a tag |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /analytics/box-office-trends | Box office trends by decade |
| GET | /analytics/genre-ratings | Average rating by genre |
| GET | /analytics/rating-distribution | Rating distribution |
| GET | /analytics/recommend?genre= | Movie recommendations |

## Data Sources

- **TMDB API**: https://www.themoviedb.org/documentation/api
- **Kaggle Dataset**: Movie Industry Dataset by Daniel Grijalva (CC0 License)

## API Documentation

See `api_docs.pdf` in the repository root.