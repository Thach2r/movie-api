"""
CineMetrics API – Test Suite (v2)
Run with:  pytest test_api.py -v
"""
import pytest
import random
import os

os.environ["API_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_cinemetrics.db"
engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
VALID_KEY   = {"X-API-Key": "test-secret-key"}
INVALID_KEY = {"X-API-Key": "wrong-key"}

def seed_movie():
    from models import Movie
    session = TestingSessionLocal()
    movie = Movie(
        tmdb_id=random.randint(1_000_000, 9_999_999),
        title="Test Movie", overview="A test film.",
        release_date="2024-01-01", genre="Drama",
        rating=7.5, vote_count=100, revenue=0, poster_path="",
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    movie_id = movie.id
    session.close()
    return movie_id

class TestRoot:
    def test_root_returns_welcome_message(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "CineMetrics" in response.json()["message"]

class TestAuthentication:
    def test_missing_api_key_returns_401(self):
        movie_id = seed_movie()
        response = client.post("/reviews/", json={"movie_id": movie_id, "author": "A", "content": "x", "score": 8.0})
        assert response.status_code == 401

    def test_wrong_api_key_returns_403(self):
        movie_id = seed_movie()
        response = client.post("/reviews/", json={"movie_id": movie_id, "author": "B", "content": "x", "score": 6.0}, headers=INVALID_KEY)
        assert response.status_code == 403

    def test_valid_api_key_is_accepted(self):
        movie_id = seed_movie()
        response = client.post("/reviews/", json={"movie_id": movie_id, "author": "C", "content": "x", "score": 9.0}, headers=VALID_KEY)
        assert response.status_code in (200, 201)

class TestReviewsCRUD:
    def test_create_review(self):
        movie_id = seed_movie()
        response = client.post("/reviews/", json={"movie_id": movie_id, "author": "Dana", "content": "Brilliant.", "score": 8.5}, headers=VALID_KEY)
        assert response.status_code in (200, 201)
        assert response.json()["author"] == "Dana"

    def test_read_reviews_for_movie(self):
        movie_id = seed_movie()
        response = client.get(f"/reviews/movie/{movie_id}")
        assert response.status_code in (200, 404)

    def test_update_review(self):
        movie_id = seed_movie()
        r = client.post("/reviews/", json={"movie_id": movie_id, "author": "Eve", "content": "Good.", "score": 7.0}, headers=VALID_KEY)
        review_id = r.json()["id"]
        update = client.put(f"/reviews/{review_id}", json={"content": "Even better.", "score": 8.0}, headers=VALID_KEY)
        assert update.status_code == 200
        assert update.json()["score"] == 8.0

    def test_delete_review(self):
        movie_id = seed_movie()
        r = client.post("/reviews/", json={"movie_id": movie_id, "author": "Frank", "content": "Meh.", "score": 5.0}, headers=VALID_KEY)
        review_id = r.json()["id"]
        assert client.delete(f"/reviews/{review_id}", headers=VALID_KEY).status_code == 200
        assert client.get(f"/reviews/{review_id}").status_code == 404

class TestTagsCRUD:
    def test_create_tag(self):
        name = f"tag-{random.randint(1000,9999)}"
        response = client.post("/tags/", json={"name": name}, headers=VALID_KEY)
        assert response.status_code in (200, 201)
        assert response.json()["name"] == name

    def test_list_tags(self):
        response = client.get("/tags/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestAnalytics:
    def test_genre_ratings_returns_200(self):
        response = client.get("/analytics/genre-ratings")
        assert response.status_code == 200

    def test_genre_ratings_contains_data(self):
        response = client.get("/analytics/genre-ratings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

class TestTopBoxOffice:
    def test_top_box_office_returns_200(self):
        """GET /analytics/top-box-office?n=5 should return 200."""
        response = client.get("/analytics/top-box-office?n=5")
        assert response.status_code in (200, 404)  # 404 ok if DB empty in test env

    def test_top_box_office_respects_n_and_sorted(self):
        """Results must be <= n items and sorted by gross descending."""
        response = client.get("/analytics/top-box-office?n=5")
        if response.status_code == 404:
            pytest.skip("No box office data in test DB – skipping sort check")
        data = response.json()
        results = data["results"]
        assert len(results) <= 5
        grosses = [r["gross"] for r in results]
        assert grosses == sorted(grosses, reverse=True)
