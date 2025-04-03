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

https://fastapi.tiangolo.com/tutorial/path-params/
https://fastapi.tiangolo.com/tutorial/query-params/
https://fastapi.tiangolo.com/tutorial/body/


