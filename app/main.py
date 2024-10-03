from fastapi import FastAPI
from app.routers import author, book
from app.database import init_redis
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BE Management Book",
    description="This is a BE Management Book.",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup_event():
#     await init_redis()

@app.get("/")
async def index():
    return {"message": "BE Management Book"}

app.include_router(author.router)
app.include_router(book.router)
