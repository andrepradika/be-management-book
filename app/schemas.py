from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BookBase(BaseModel):
    title: str
    description: Optional[str]
    publish_date: Optional[date]
    author_id: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True  

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str]
    birth_date: Optional[date]

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    books: List[Book] = []

    class Config:
        orm_mode = True
