from sqlalchemy.orm import Session
from init_schema import engine, User


user1 = User(
        username="user1",
        hashed_password="akjsdflakjsfh",
        email="user@one.com",
        active=True
        )

user2 = User(
        username="user2",
        hashed_password="akjsdflakjsfh",
        email="user@two.com",
        active=False
        )


with Session(engine) as session:
    session.add(user1)
    session.add(user2)
    session.commit()
