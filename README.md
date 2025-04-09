# Some theory

## Abstraction

Hide the implementation and only show necessary details to the user.

```Python
class Circle():
    """docstring for Circle."""

    def __init__(self, radius):
        super(Circle, self).__init__()
        self.r = radius

    def circumference(self):
        """ This method is abstracted """
        return 2*3.14*self.r


if __name__ == "__main__":
    c = Circle(12.3)
    print(c.circumference())
```

We don't have to know how the `circumference()` method works - it's abstracted.

---

## Encapsulation

- Changes public attributes to private.
- How?
- Use the `__` (double underscore) notation in class properties.

```Python
class Circle:
	def __init__(self, radius):
		self.__r = radius # This is not encapsulated and cannot change
		self.diameter = 2*radius

	def get_rad(self):
		return self.__r
```

**When we use private variables, we need to create getters and setters for the private variable(s).**

---

## Inheritance

- A class inherits all properties and methods of another class.
- It's a fundamental OOP concept.
- Enable overwriting.

**This creates an "is-a" relationship between objects.**

```Python
class Animal:
	def __init__(self, animal_class, weight):
		self.__animal_class = animal_class
		self.weight = weight

	def talk(self):
		print("Blah")

class Dog(Animal):
	super().__init__(animal_class, weight)

	def talk(self): # Overwrites
		print("Bark")

class Cat(Animal):
	super().__init__(animal_class, weight)

	def talk(self): # Overwrites
		print("Meoww")
```

The `Animal` **is-a** `Dog` and the `Dog` **is-a** `Animal`.

---

## Polymorphism

- Have many forms?

- In this case, `speak()` can have many forms, it can both be a dog and a cat.

```Python

def speak(a: Animal):
	a.talk()

speak(cat)
speak(dog)
```

---

## Composition

- A way to create objects made up of other objects.

- **This creates a "HAS-A" relationship between the objects.**

```Python
class Engine():
	pass

class Vehicle():
	def __init__(self, engine):
		engine = engine

e = Engine()
v = Vehicle(e)
```

The vehicles **has-a** engine.

---

## CRUD operations

- `Create`
- `Read`
- `Update`
- `Delete`

---

## HTTP methods

| Operation | Method |
| --------- | ------ |
| Read      | GET    |
| Create    | POST   |
| Update    | PUT    |
| Delete    | DELETE |

---

# FastAPI

- https://fastapi.tiangolo.com/tutorial/path-params/
- https://fastapi.tiangolo.com/tutorial/query-params/
- https://fastapi.tiangolo.com/tutorial/body/

---

# SQLAlchemy

- Is an ORM - Object Relational Mapper.
- Supports many relational DBMS - Database Management Systems
- Abstracts SQL from the DBMS

---
# SQL Operations

SQL commands correspond to HTTP operations - CRUD. These operations have the following syntax.


#### **INSERT** - Create

To insert data use `INSERT INTO` and `VALUES`.

```SQL
INSERT INTO todos (title, description, priority, complete, ...)

VALUES ("Groceries", "Do the groceries", 3, False, ...);
```


#### **SELECT** - Read

To extract data use `SELECT`. Use `*` to fetch all rows and columns or specific ones.

```SQL
SELECT * FROM todos;
SELECT title, description FROM todos;
```


#### **WHERE**

Specify criteria with `WHERE`.

```SQL
SELECT * from todos WHERE priority=5;
SELECT * from todos where title="Groceries";
SELECT * from todos where id=2;
```


#### **UPDATE** - Update

Update records.

```SQL
UPDATE todos SET complete=True WHERE id=5;
UPDATE todos SET complete=True WHERE title="Groceries";
UPDATE todos set complete=False WHERE id=9;
```

#### **DELETE** - Delete

Delete records

```SQL
DELETE FROM todos WHERE id=4;
DELETE FROM todos WHERE complete=1;
```


# Authentication - password flow

The user sends a `POST` request to `/login` API endpoint.
The request contains the `username` and `password` of the user.

The application performs the Login flow:

1. Authenticate user
    1.1 Verify the user exists in the database (based on the `username`)
        1.1.1 If the username is in the database return the UserInDB object
        1.1.2 If the username does not exists in the database return `None`
    1.2 Verify the provided password with the stored hashed password
        1.2.1 If verification is False, raise `exception`
    1.3 Return user item from database
2. Generate JWT token using the user item
    2.1 Initialize data: `{"sub": username}`
    2.2 Add token expiration time: `{"exp": time_delta}`
    2.3 Join the above into a single dict (`update()`)
    2.4 Encode it using: `jwt.encode()`
    2.5 Create the JWT token object with `access_token` and `token_type` fields
    2.6 Return the JWT token object to the client


