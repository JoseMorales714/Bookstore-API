from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from book import Book

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "detail": exc.errors()}
    )

@app.post("/books/")
async def create_book(book: Book):
    return {"message": "Book created successfully"}
