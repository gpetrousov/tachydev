"""
This code consists of 3 sections:
    1. Creation of ORM models

    2. Creation of a connection to the database engine

    3. Initialization of the schema

We need to run this code once only to initialize our tables. Once initialized
we can connect to the database and run SQL commands on it. You can execute this
script just with the python interpreter.

```shell
python xxx.py
```

Example:
```SQL
sqlite3 sqlite.db                                                                                                                    master@singularity
sqlite> .schema
CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(20) NOT NULL,
        hashed_password VARCHAR NOT NULL,
        email VARCHAR(30) NOT NULL,
        active BOOLEAN NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (username)
);
sqlite> select * from users;
sqlite> INSERT INTO users (username, hashed_password, email, active) VALUES ('ipetrousov', '$2b.alkfjadf.dsfja;k.3294uid', 'contact@petrousoft.com', True);
sqlite> select * from users;
1|ipetrousov|$2b.alkfjadf.dsfja;k.3294uid|contact@petrousoft.com|1
```
"""

from sqlalchemy import create_engine, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 1. Create ORM models
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


# 2. establish connectivity to the engine
engine = create_engine("sqlite:///user_management.db", echo=True)

# 3. create database schema - once
Base.metadata.create_all(bind=engine)
