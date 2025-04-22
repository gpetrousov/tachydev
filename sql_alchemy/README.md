# Structure

1. `init_schema.py`

Generate the schema the models in the database.


2. `create_session.py` - https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session

Uses the `Session` class to connet to the DB and add the data.


3. `use_sessionmaker.py` - https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker

Uses `sessionmaker()` constructor to connect to the DB and add the data.


4. `sql_operations.py` - https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html

Contains examples of most essential SQL operations using SQLAlchemy 2.0.
