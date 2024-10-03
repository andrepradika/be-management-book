from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, dependencies, utils
from app.database import get_db
from typing import List
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/authors",
    tags=["authors"]
)

@router.get("/", response_model=List[schemas.Author])
async def get_authors(db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    # await utils.set_cache("authors_list", None)
    cache_key = "authors_list"
    cached_authors = await utils.get_cache(cache_key)
    if cached_authors:
        return cached_authors
    authors = db.query(models.Author).options(joinedload(models.Author.books)).all()
    await utils.set_cache(cache_key, authors)
    return authors

@router.post("/", response_model=schemas.Author)
async def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    new_author = models.Author(**author.dict())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    await utils.set_cache("authors_list", None)
    return new_author

@router.get("/{id}", response_model=schemas.Author)
async def get_author(id: int, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    author = db.query(models.Author).filter(models.Author.id == id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@router.put("/{id}", response_model=schemas.Author)
async def update_author(id: int, author: schemas.AuthorCreate, db: Session = Depends(get_db), token: str = Depends(dependencies.get_bearer_token)):
    db_author = db.query(models.Author).filter(models.Author.id == id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in author.dict().items():
        setattr(db_author, key, value)
    db.commit()
    db.refresh(db_author)
    await utils.set_cache("authors_list", None)
    return db_author

@router.delete("/{author_id}")
async def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if author.books:
        raise HTTPException(status_code=400, detail="Cannot delete author with associated books")
    db.delete(author)
    db.commit()
    return {"detail": "Author deleted successfully"}

@router.get("/{id}/books", response_model=List[schemas.Book])
async def get_books_by_author(
    id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(dependencies.get_bearer_token)
):
    # Fetch books written by the author with the given ID
    books = db.query(models.Book).filter(models.Book.author_id == id).all()
    
    if not books:
        raise HTTPException(status_code=404, detail="No books found for this author")
    
    return books