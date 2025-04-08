from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status


class Book:
    id: int
    title: str
    author: str
    category: str
    rating: int
    year: int

    def __init__(self, id, title, author, category, rating, year):
        self.id = id
        self.title = title
        self.author = author
        self.category = category
        self.rating = rating
        self.year = year


class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="Optional ID field;Incremental based on last object's ID.'")
    title: str = Field(min_length=3)
    author: str = Field(min_length=2)
    category: str = Field(min_length=4)
    rating: int = Field(gt=0, lt=6)
    year: int

    model_config = {
            "json_schema_extra": {
                "example": {
                    "title": "LORT",
                    "author": "Tokien",
                    "category": "Fantasy",
                    "rating": "5",
                    "year": "1954"
                    }
                }
            }


BOOKS = [
        Book(1, "The Unicorn Project", "Gim Kene", "Novel", 5, 2019),
        Book(2, "The Phoenix Project", "Gim Kene", "Novel", 5, 2013),
        Book(3, "Elon Musk", "Ashlee Vance", "Biography", 4, 2015),
        Book(4, "Can't Hurt Me", "David Goggins", "Biography", 5, 2018),
        Book(5, "Brief Answers to the Big Questions", "Stephen Hawking", "Science", 5, 2018),
        Book(6, "Neuromancer", "William Gibson", "Sci-Fi", 3, 1984),
        ]


app = FastAPI()


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    """ Path parameter method. """
    for b in BOOKS:
        if b.id == book_id:
            return b
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/books/year/{year}", status_code=status.HTTP_200_OK)
async def get_books_by_year(year: int):
    book_to_return = []
    for b in BOOKS:
        if b.year == year:
            book_to_return.append(b)
    if len(book_to_return) == 0:
        raise HTTPException(status_code=404, detail="No books matching year found")
    return book_to_return


@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for b in BOOKS:
        if b.rating == book_rating:
            books_to_return.append(b)
    if len(books_to_return) == 0:
        raise HTTPException(status_code=404, detail="No books matching rating found")
    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    print(f"Before: {type(book_request)}")
    new_book = Book(**book_request.model_dump())
    print(f"After: {type(new_book)}")
    BOOKS.append(set_new_book_id(new_book))


@app.put("/update-book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book_by_id(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            return
    raise HTTPException(status_code=404, detail="Book by ID not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


def set_new_book_id(book: Book):
    book.id = BOOKS[-1].id+1 if len(BOOKS) > 0 else 1
    return book
