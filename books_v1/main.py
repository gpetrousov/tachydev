from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
        {
            "title": "The Unicorn Project",
            "author": "Gim Kene",
            "category": "Novel"
            },
        {
            "title": "The Phoenix Project",
            "author": "Gim Kene",
            "category": "Novel"
         },
        {
            "title": "Elon Musk",
            "author": "Ashlee Vance",
            "category": "Biography"
         },
        {
            "title": "Can't Hurt Me",
            "author": "David Goggins",
            "category": "Biography"
         },
        {
            "title": "Brief Answers to the Big Questions",
            "author": "Stephen Hawking",
            "category": "Science"
         }
        ]


"""
GET Methods
"""


@app.get("/books")
async def get_all_books():
    return BOOKS


@app.get("/books/{author}")
async def get_books_by_author(author: str):
    """ Path parameter """
    books_to_return = []
    for b in BOOKS:
        if b.get("author").lower() == author.lower():
            books_to_return.append(b)
    return books_to_return


# This will conflict with the get from above because it's executed over it.
# @app.get("/books/{category}")
# async def get_books_by_category(category: str):
#     books_to_return = []
#     for b in BOOKS:
#         if b.get("category").lower() == category.lower():
#             books_to_return.append(b)
#     return books_to_return


@app.get("/books/")
async def get_books_by_category_query(category: str):
    """ Query parameter """
    books_to_return = []
    for b in BOOKS:
        if b.get("category").lower() == category.lower():
            books_to_return.append(b)
    return books_to_return


@app.get("/books/{author}/")
async def get_books_by_author_path_and_title_query(author: str, title: str):
    """ Query and Path parameter """
    books_to_return = []
    for b in BOOKS:
        if b.get("author").lower() == author.lower():
            if b.get("title").lower() == title.lower():
                books_to_return.append(b)
    return books_to_return


"""
POST Methods
"""


@app.post("/books/create_book/")
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)


"""
UPDATE Methods
"""


@app.put("/books/update_book/")
async def update_book_by_title(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book


"""
DELETE Methods
"""


@app.delete("/books/delete_book/{book_title}")
async def delete_book_by_title(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold == book_title.casefold:
            BOOKS.pop(i)
