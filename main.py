from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException
from fastapi.param_functions import Body, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from book import Book

app = FastAPI()

## app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client.books

@app.get("/")
async def root():
    return {"message": "Hello my guy"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "detail": exc.errors()}
    )

# @app.post("/books/")
# async def create_book(BaseModel: book):
#     return {"message": "Book created successfully"}

# API endpoint to add a new book
@app.post("/books", response_model=Book)
async def create_book(book: Book):
    # Create a new Book document in MongoDB
    book_dict = book.dict()
    result = await db.books.insert_one(book_dict)
    created_book = await db.books.find_one({"_id": result.inserted_id})
    return Book(**created_book)

# API endpoint to retrieve all books
@app.get("/books", response_model=List[Book])
async def get_books():
    books = []
    async for book in db.books.find():
        books.append(Book(**book))
    return books

# API endpoint to retrieve a specific book by ID
@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = await db.books.find_one({"_id": ObjectId(book_id)})
    if book:
        return Book(**book)
    else:
        raise HTTPException(status_code=404, detail="Book not found")

# API endpoint to update an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    """
    Update a book by ID
    """
    try:
        updated_book = await db.books.find_one_and_replace({"_id": ObjectId(book_id)}, book.dict())
        return templates.TemplateResponse("book.html", {"request": request, "book": updated_book})
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"message": str(e)})    
    return {"message": "Book updated successfully"}

# API endpoint to delete a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    """
    Delete a book by ID
    """
    try:
        deleted_book = await db.books.find_one_and_delete({"_id": ObjectId(book_id)})
        if not deleted_book:
            raise HTTPException(status_code=404, detail="Book not found")
        return RedirectResponse(url="/books")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"message": str(e)})
    return {"message": "Book deleted successfully"}

# API endpoint to search for books by title, author, and price range
@app.get("/search")
async def search_books(title: str = "", author: str = "", min_price: float = 0, max_price: float = 1000):
    """
    Search for books by title, author, and price range
    """
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    query["price"] = {"$gte": min_price, "$lte": max_price}
    books = await db.books.find(query).to_list(length=1000)
    return books

