from fastapi import FastAPI, HTTPException,Response
import json
from typing import List
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel
from book import Book

# Create a FastAPI instance
app = FastAPI()



# Connect to the MongoDB database
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.bookstore
book_collection = db.books

print("Connected")
@app.get("/")
async def root():
    return {"message": "Welcome to the Bookstore API!"}

@app.get("/favicon.ico")
async def favicon():
    # Return a 204 No Content response for favicon.ico requests
    return Response(status_code=204)
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
    updated_book = await db.books.find_one_and_replace({"_id": ObjectId(book_id)}, book.dict())
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated successfully"}

# API endpoint to delete a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    """
    Delete a book by ID
    """
    deleted_book = await db.books.find_one_and_delete({"_id": ObjectId(book_id)})
    if not deleted_book:
        raise HTTPException(status_code=404, detail="Book not found")
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
    result = await book_collection.find(query).to_list(length=100)
    for book in result:
        book["_id"] = str(book["_id"])

    return result
# Aggregation

# Get Top 5 bestselling books
@app.get("/bestsellers")
async def get_bestseller():
    pipeline = [
        {"$sort": {"sold": -1}},
        {"$limit": 5}
    ]
    top_books = await db.books.aggregate(pipeline).to_list(length=5)
    # Convert the ObjectId to a string representation
    for book in top_books:
        book["_id"] = str(book["_id"])

    return top_books

# Top 5 author with the most books in the store
@app.get("/best-authors")
async def get_authors():
    top_authors_pipeline = [
        {"$group": {"_id": "$author", "stock": {"$sum": 1}}},
        {"$sort": {"stock": -1}},
        {"$limit": 5}
    ]
    top_authors = await db.books.aggregate(top_authors_pipeline).to_list(length=None)
    return top_authors

# Total number of books in the store
@app.get("/total")
async def total_books():
    total_books_pipeline = [
        {"$group": {"_id": None, "count": {"$sum": 1}}}
    ]
    total_books_result = await db.books.aggregate(total_books_pipeline).to_list(length=None)
    total_books = total_books_result[0]["count"]
    return total_books
