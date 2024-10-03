import pytest
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

@pytest.fixture(scope="session", autouse=True)
def teardown():
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_author_data():
    return {
        "name": "Test Author",
        "bio": "This is a test author.",
        "birth_date": "1980-01-01",
    }

@pytest.fixture(scope="module")
def test_book_data(create_author):
    return {
        "title": "Test Book",
        "description": "This is a test book.",
        "publish_date": "2024-01-01",
        "author_id": create_author["id"]  # Use the created author's ID
    }

@pytest.fixture(scope="module")
def create_author(test_author_data):
    with patch("app.utils.get_cache", return_value=None), patch("app.utils.set_cache"):
        response = client.post("/authors/", json=test_author_data, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200  # Check for successful creation
        return response.json()

@pytest.fixture(scope="module")
def create_book(create_author, test_book_data):
    with patch("app.utils.get_cache", return_value=None), patch("app.utils.set_cache"):
        response = client.post("/books/", json=test_book_data, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200  # Ensure book creation is successful
        book = response.json()
        print("Created book:", book)  # Print book details for debugging
        return book


def test_get_books_by_author(create_author, create_book):
    author_id = create_author["id"]

    # Verify that the book exists in the database
    response = client.get(f"/books/{create_book['id']}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["author_id"] == author_id  # Ensure the book's author_id matches

    response = client.get(f"/authors/{author_id}/books", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1  # Expecting one book
    assert response.json()[0]["title"] == create_book["title"]

def test_get_books(create_book):
    with patch("app.utils.get_cache", return_value=None), patch("app.utils.set_cache"):
        response = client.get("/books/", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0  # Ensure there are books in the list


def test_get_book(create_book):
    book_id = create_book["id"]
    with patch("app.utils.get_cache", return_value=None):
        response = client.get(f"/books/{book_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["title"] == create_book["title"]

def test_update_book(create_book):
    book_id = create_book["id"]
    updated_data = {
        "title": "Updated Test Book",
        "description": "This book has been updated.",
        "publish_date": "2024-01-02",
        "author_id": create_book["author_id"]
    }
    with patch("app.utils.get_cache", return_value=None), patch("app.utils.set_cache"):
        response = client.put(f"/books/{book_id}", json=updated_data, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["title"] == updated_data["title"]

def test_delete_book(create_book):
    book_id = create_book["id"]
    with patch("app.utils.get_cache", return_value=None), patch("app.utils.set_cache"):
        response = client.delete(f"/books/{book_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 200
        assert response.json()["message"] == "Book deleted successfully"

        # Attempt to get the deleted book
        response = client.get(f"/books/{book_id}", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
        assert response.status_code == 404
