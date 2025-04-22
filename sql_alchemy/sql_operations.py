from use_sessionmaker import Session
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from init_schema import User


# INSERT - Create
with Session() as sess:
    print("\n=====INSERT - Create=====")
    print("=============Insert CORE approach:")
    try:
        # ORM level function
        sess.add(
                User(
                    username="user5",
                    hashed_password="(*&#*URILfhfl",
                    email="user@five.com",
                    )
                )
        # Persist changes
        sess.commit()
    except:
        print("=========Users present")

with Session() as sess:
    print("=============Insert ORM approach:")
    try:
        orm_insert_statement = (
                insert(User).values(
                    username="yannis",
                    hashed_password="kadj;aklf",
                    email="contact@petrousoft.com"
                    )
                )
        sess.execute(orm_insert_statement)
        sess.commit()
    except IntegrityError as e:
        print(f"Error inserting user 'yannis': {e}")
        sess.rollback()  # Rollback the transaction in case of an error
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sess.rollback()
    print("=====ENDS\n")

# SELECT - Read
with Session() as sess:
    print("\n=====SELECT - READ=====")

    orm_select_statement = select(User)
    print(f"ORM select statement:{orm_select_statement}")
    result = sess.execute(orm_select_statement) # Returns a Result object - a sequence of Row objects.
    users = result.scalars() # Produces a ScalarResult instance - all scalar values in a sequence.
    print(">ALL USERS:")
    for u in users:
        print(f"id: {u.id}, username:{u.username}, hashed_password:{u.hashed_password}, email:{u.email}, active:{u.active}")
    print("=====ENDS\n")

    # Expects one result - raise exception otherwise
    orm_select_one_statement = select(User).where(User.username == "user1")
    print(f"ORM select one statement:{orm_select_one_statement}")
    result = sess.execute(orm_select_one_statement)
    scalar = result.scalar_one() # Return exactly one scalar result or None.
    print(">ONE USER:")
    print(f"id: {scalar.id}, username: {scalar.username}, hashed_password:{scalar.hashed_password}, email:{scalar.email}, active:{scalar.active}")
    print("=====ENDS\n")

    # Return the first element - don't raise exception
    orm_select_first_statement = select(User).where(User.id == 4)
    result = sess.execute(orm_select_first_statement)
    first_row = result.scalar()
    print(">FIRST ROW RESULT:")
    print(f"username: {first_row.username}, hashed_password:{first_row.hashed_password}, email:{first_row.email}, active:{first_row.active}")
    print("=====ENDS\n")

# UPDATE - Update
with Session() as sess:
    print("\n=====UPDATE - Update=====")
    orm_update_using_where_statement = (
            update(User).where(
                User.username == "yannis").values(
                    hashed_password="sUp3r53kr37"
                    )
                )
    print(f">Update using with ORM statement:{orm_update_using_where_statement}")
    try:
        sess.execute(orm_update_using_where_statement)
        sess.commit()
    except Exception as e:
        print(f"Update errror: {e}")
        sess.rollback()
    print("=====ENDS\n")

# DELETE - Delete
with Session() as sess:
    print("\n=====DELETE - Delete=====")
    try:
        orm_delete_usign_where_statement = (
                delete(User).where(
                    User.username == "yannis"
                    )
                )
        print(f">Delete using where ORM statement: {orm_delete_usign_where_statement}")
        sess.execute(orm_delete_usign_where_statement)
        sess.commit()
    except Exception as e:
        print(f"Delete error: {e}")

with Session() as sess:
    try:
        orm_delete_usign_in_statement = (
                delete(User).where(
                    User.username.in_(["user5"])))
        print(f">Delete using IN ORM statement: {orm_delete_usign_in_statement}")
        sess.execute(orm_delete_usign_in_statement)
        sess.commit()
    except Exception as e:
        print(f"Delete error: {e}")
    print("=====ENDS\n")
