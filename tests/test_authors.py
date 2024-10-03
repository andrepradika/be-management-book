import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.main import app
from app.models import Base
from unittest.mock import patch

# Set up the testing database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency override for testing
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

client = TestClient(app)

# Bearer token for authentication
BEARER_TOKEN = "supersecrettoken123"

@pytest.fixture(scope="module")
def test_author_data():
    return {
        "name": "Test Author",
        "bio": "This is a test author.",
        "birth_date": "1980-01-01",
    }

@pytest.fixture(scope="module")
def create_author(test_author_data):
    with patch("app.utils.get_cache") as mock_get_cache, patch("app.utils.set_cache") as mock_set_cache:
        mock_get_cache.return_value = None  # Simulate no cache
        response = client.post("/authors/", json=test_author_data, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        return response.json()

def test_get_authors(create_author):
    with patch("app.utils.get_cache") as mock_get_cache:
        mock_get_cache.return_value = None  # Simulate no cache
        response = client.get("/authors/", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_get_author(create_author):
    author_id = create_author["id"]
    with patch("app.utils.get_cache") as mock_get_cache:
        mock_get_cache.return_value = None  # Simulate no cache
        response = client.get(f"/authors/{author_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["name"] == create_author["name"]

def test_update_author(create_author):
    author_id = create_author["id"]
    updated_data = {
        "name": "Updated Author",
        "bio": "This author has been updated.",
        "birth_date": "1980-01-01",
    }
    with patch("app.utils.get_cache") as mock_get_cache, patch("app.utils.set_cache") as mock_set_cache:
        mock_get_cache.return_value = None  # Simulate no cache
        response = client.put(f"/authors/{author_id}", json=updated_data, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["name"] == updated_data["name"]

def test_delete_author(create_author):
    author_id = create_author["id"]
    with patch("app.utils.get_cache") as mock_get_cache, patch("app.utils.set_cache") as mock_set_cache:
        mock_get_cache.return_value = None  # Simulate no cache
        response = client.delete(f"/authors/{author_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["detail"] == "Author deleted successfully"

        # Attempt to get the deleted author
        response = client.get(f"/authors/{author_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 404