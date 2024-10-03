from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, dependencies, utils
from app.database import get_db
from typing import List
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.get("/", response_model=List[schemas.Book])
async def get_books(db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    cache_key = "books_list"
    cached_books = await utils.get_cache(cache_key)
    if cached_books:
        return cached_books
    books = db.query(models.Book).options(joinedload(models.Book.author)).all() 
    serialized_books = [schemas.Book.from_orm(book) for book in books]  
    await utils.set_cache(cache_key, serialized_books)
    return serialized_books


@router.post("/", response_model=schemas.Book)
async def create_book(
    book: schemas.BookCreate, 
    db: Session = Depends(get_db), 
    token: str = Depends(dependencies.get_bearer_token)):
    author = db.query(models.Author).filter(models.Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    await utils.set_cache("books_list", None)
    await utils.set_cache("authors_list", None)
    return new_book

@router.get("/{id}", response_model=schemas.Book)
async def get_book(id: int, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=schemas.Book)
async def update_book(id: int, book: schemas.BookCreate, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    await utils.set_cache("books_list", None)
    await utils.set_cache("authors_list", None)
    return db_book

@router.delete("/{id}")
async def delete_book(id: int, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    await utils.set_cache("books_list", None)
    await utils.set_cache("authors_list", None)
    return {"message": "Book deleted successfully"}
