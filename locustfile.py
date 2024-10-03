from locust import HttpUser, task, between
import json

class FastAPIUser(HttpUser):
    # Simulates the wait time between tasks
    wait_time = between(1, 5)

    def on_start(self):
        """This is run when the simulated user starts."""
        self.token = self.get_auth_token()
        self.author_id = None
        self.book_id = None

    def get_auth_token(self):
        # Replace this with an actual call to obtain the token if your API requires authentication
        return "supersecrettoken123"

    # Author-related tasks
    @task
    def create_author(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Create a new author
        author_payload = {
            "name": "New Author",
            "bio": "Temporary author for testing",
            "birth_date": "1980-01-01"
        }
        
        response = self.client.post("/authors/", json=author_payload, headers=headers)
        
        if response.status_code == 200:
            new_author = response.json()
            self.author_id = new_author['id']
            # print(f"Created author: {self.author_id}")
            pass
        else:
            print(f"Failed to create author - {response.status_code}")

    @task
    def get_authors(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        # Retrieve a list of all authors
        response = self.client.get("/authors/", headers=headers)
        if response.status_code == 200:
            # print("Retrieved authors:", response.json())
            pass
        else:
            print(f"Failed to retrieve authors - {response.status_code}")

    @task
    def get_single_author(self):
        if self.author_id:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            # Retrieve details of a specific author
            response = self.client.get(f"/authors/{self.author_id}", headers=headers)
            if response.status_code == 200:
                # print(f"Retrieved author with ID {self.author_id}: {response.json()}")
                pass
            else:
                print(f"Failed to retrieve author {self.author_id} - {response.status_code}")

    @task
    def update_author(self):
        if self.author_id:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            # Update an existing author
            payload = {
                "name": "Updated Author",
                "bio": "Updated bio",
                "birth_date": "1985-05-15"
            }
            response = self.client.put(f"/authors/{self.author_id}", json=payload, headers=headers)
            if response.status_code == 200:
                # print(f"Successfully updated author: {self.author_id}")
                pass
            else:
                print(f"Failed to update author {self.author_id} - {response.status_code}")

    @task
    def delete_author(self):
        if self.author_id:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            # Delete an author
            response = self.client.delete(f"/authors/{self.author_id}", headers=headers)
            if response.status_code == 200:
                print(f"Successfully deleted author: {self.author_id}")
                self.author_id = None  # Reset author_id after deletion
            else:
                print(f"Failed to delete author {self.author_id} - {response.status_code}")

    # Book-related tasks
    @task
    def create_book(self):
        if self.author_id:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            # Create a new book for the created author
            from datetime import datetime

            # Create a valid publish date
            publish_date = datetime.now().date().isoformat()  # e.g., '2024-01-01'
            book_payload = {
                "title": "New Test Book",
                "description": "A brief description for the test book.",
                "publish_date": publish_date,
                "author_id": self.author_id
            }
            response = self.client.post("/books/", json=book_payload, headers=headers)
            if response.status_code == 200:
                new_book = response.json()
                self.book_id = new_book['id']
                # print(f"Successfully created book: {self.book_id}")
                pass
            else:
                print(f"Failed to create book - {response}")

    @task
    def get_books(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        # Retrieve a list of all books
        response = self.client.get("/books/", headers=headers)
        if response.status_code == 200:
            # print("Retrieved books:", response.json())
            pass
        else:
            print(f"Failed to retrieve books - {response.status_code}")

    @task
    def get_single_book(self):
        if self.book_id:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            # Retrieve details of a specific book
            response = self.client.get(f"/books/{self.book_id}", headers=headers)
            if response.status_code == 200:
                # print(f"Retrieved book with ID {self.book_id}: {response.json()}")
                pass
            else:
                print(f"Failed to retrieve book {self.book_id} - {response.status_code}")

    @task
    def update_book(self):
        if self.book_id and self.author_id:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            # Update an existing book
            payload = {
                "title": "Updated Test Book",
                "author_id": self.author_id,
                "description": "An updated description for the test book.",
                "published_date": "2024-02-01"
            }
            response = self.client.put(f"/books/{self.book_id}", json=payload, headers=headers)
            if response.status_code == 200:
                # print(f"Successfully updated book: {self.book_id}")
                pass
            else:
                print(f"Failed to update book {self.book_id} - {response.status_code}")

    @task
    def delete_book(self):
        if self.book_id:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            # Delete a book
            response = self.client.delete(f"/books/{self.book_id}", headers=headers)
            if response.status_code == 200:
                # print(f"Successfully deleted book: {self.book_id}")
                self.book_id = None  # Reset book_id after deletion
            else:
                print(f"Failed to delete book {self.book_id} - {response.status_code}")

