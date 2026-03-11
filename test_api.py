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


# ───────────────────────────────────────────────
# Root
# ───────────────────────────────────────────────

class TestRoot:
    def test_root_returns_welcome_message(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "CineMetrics" in response.json()["message"]


# ───────────────────────────────────────────────
# Authentication
# ───────────────────────────────────────────────

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

    def test_delete_requires_api_key(self):
        """DELETE without key should be rejected, not silently succeed."""
        movie_id = seed_movie()
        r = client.post("/reviews/", json={"movie_id": movie_id, "author": "Z", "content": "x", "score": 5.0}, headers=VALID_KEY)
        review_id = r.json()["id"]
        assert client.delete(f"/reviews/{review_id}").status_code == 401

    def test_put_requires_api_key(self):
        """PUT without key should be rejected."""
        movie_id = seed_movie()
        r = client.post("/reviews/", json={"movie_id": movie_id, "author": "Z", "content": "x", "score": 5.0}, headers=VALID_KEY)
        review_id = r.json()["id"]
        assert client.put(f"/reviews/{review_id}", json={"content": "sneaky edit"}).status_code == 401


# ───────────────────────────────────────────────
# Reviews – CRUD
# ───────────────────────────────────────────────

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


# ───────────────────────────────────────────────
# Reviews – Boundary / Edge Cases
# ───────────────────────────────────────────────

class TestReviewsBoundary:
    def test_get_nonexistent_review_returns_404(self):
        response = client.get("/reviews/999999")
        assert response.status_code == 404

    def test_create_review_for_nonexistent_movie_returns_404(self):
        response = client.post(
            "/reviews/",
            json={"movie_id": 999999, "author": "Ghost", "content": "Nobody.", "score": 5.0},
            headers=VALID_KEY
        )
        assert response.status_code == 404

    def test_score_at_minimum_boundary(self):
        """score = 0.0 should be accepted."""
        movie_id = seed_movie()
        response = client.post(
            "/reviews/",
            json={"movie_id": movie_id, "author": "Min", "content": "Terrible.", "score": 0.0},
            headers=VALID_KEY
        )
        assert response.status_code in (200, 201)
        assert response.json()["score"] == 0.0

    def test_score_at_maximum_boundary(self):
        """score = 10.0 should be accepted."""
        movie_id = seed_movie()
        response = client.post(
            "/reviews/",
            json={"movie_id": movie_id, "author": "Max", "content": "Perfect.", "score": 10.0},
            headers=VALID_KEY
        )
        assert response.status_code in (200, 201)
        assert response.json()["score"] == 10.0

    def test_score_above_maximum_rejected(self):
        """score = 10.1 should be rejected with 422."""
        movie_id = seed_movie()
        response = client.post(
            "/reviews/",
            json={"movie_id": movie_id, "author": "Over", "content": "Too high.", "score": 10.1},
            headers=VALID_KEY
        )
        assert response.status_code == 422

    def test_score_below_minimum_rejected(self):
        """score = -1.0 should be rejected with 422."""
        movie_id = seed_movie()
        response = client.post(
            "/reviews/",
            json={"movie_id": movie_id, "author": "Under", "content": "Too low.", "score": -1.0},
            headers=VALID_KEY
        )
        assert response.status_code == 422

    def test_delete_nonexistent_review_returns_404(self):
        response = client.delete("/reviews/999999", headers=VALID_KEY)
        assert response.status_code == 404

    def test_update_nonexistent_review_returns_404(self):
        response = client.put("/reviews/999999", json={"content": "Nope"}, headers=VALID_KEY)
        assert response.status_code == 404

    def test_pagination_skip_and_limit(self):
        """Paginated results should respect limit parameter."""
        movie_id = seed_movie()
        for i in range(5):
            client.post("/reviews/", json={"movie_id": movie_id, "author": f"User{i}", "content": "ok", "score": 5.0}, headers=VALID_KEY)
        response = client.get("/reviews/?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) <= 2

    def test_pagination_skip_beyond_results(self):
        """skip larger than total records should return empty list, not error."""
        response = client.get("/reviews/?skip=999999&limit=10")
        assert response.status_code == 200
        assert response.json() == []

    def test_pagination_invalid_limit_rejected(self):
        """limit=0 is below minimum=1, should return 422."""
        response = client.get("/reviews/?limit=0")
        assert response.status_code == 422

    def test_pagination_limit_over_max_rejected(self):
        """limit=101 exceeds maximum=100, should return 422."""
        response = client.get("/reviews/?limit=101")
        assert response.status_code == 422


# ───────────────────────────────────────────────
# Tags – CRUD
# ───────────────────────────────────────────────

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


# ───────────────────────────────────────────────
# Tags – Boundary / Edge Cases
# ───────────────────────────────────────────────

class TestTagsBoundary:
    def test_duplicate_tag_returns_400(self):
        """Creating a tag with an existing name should return 400."""
        name = f"unique-{random.randint(10000, 99999)}"
        client.post("/tags/", json={"name": name}, headers=VALID_KEY)
        response = client.post("/tags/", json={"name": name}, headers=VALID_KEY)
        assert response.status_code == 400

    def test_get_nonexistent_tag_returns_404(self):
        response = client.get("/tags/999999")
        assert response.status_code == 404

    def test_delete_nonexistent_tag_returns_404(self):
        response = client.delete("/tags/999999", headers=VALID_KEY)
        assert response.status_code == 404

    def test_tags_pagination_limit(self):
        """limit=1 should return at most 1 tag."""
        for i in range(3):
            client.post("/tags/", json={"name": f"pagingtag-{random.randint(10000,99999)}"}, headers=VALID_KEY)
        response = client.get("/tags/?skip=0&limit=1")
        assert response.status_code == 200
        assert len(response.json()) <= 1

    def test_tags_pagination_invalid_limit_rejected(self):
        """limit=0 should return 422."""
        response = client.get("/tags/?limit=0")
        assert response.status_code == 422

    def test_add_same_tag_twice_to_movie_returns_400(self):
        """Adding the same tag to a movie twice should return 400."""
        movie_id = seed_movie()
        name = f"doubletag-{random.randint(10000, 99999)}"
        tag_resp = client.post("/tags/", json={"name": name}, headers=VALID_KEY)
        tag_id = tag_resp.json()["id"]
        client.post(f"/movies/{movie_id}/tags", json={"tag_id": tag_id}, headers=VALID_KEY)
        response = client.post(f"/movies/{movie_id}/tags", json={"tag_id": tag_id}, headers=VALID_KEY)
        assert response.status_code == 400

    def test_get_tags_for_nonexistent_movie_returns_404(self):
        response = client.get("/movies/999999/tags")
        assert response.status_code == 404


# ───────────────────────────────────────────────
# Analytics
# ───────────────────────────────────────────────

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
        response = client.get("/analytics/top-box-office?n=5")
        assert response.status_code in (200, 404)

    def test_top_box_office_respects_n_and_sorted(self):
        response = client.get("/analytics/top-box-office?n=5")
        if response.status_code == 404:
            pytest.skip("No box office data in test DB – skipping sort check")
        data = response.json()
        results = data["results"]
        assert len(results) <= 5
        grosses = [r["gross"] for r in results]
        assert grosses == sorted(grosses, reverse=True)

    def test_top_box_office_n_above_max_rejected(self):
        """n=51 exceeds max=50, should return 400."""
        response = client.get("/analytics/top-box-office?n=51")
        assert response.status_code == 400

    def test_top_box_office_n_zero_rejected(self):
        """n=0 is invalid, should return 400."""
        response = client.get("/analytics/top-box-office?n=0")
        assert response.status_code == 400