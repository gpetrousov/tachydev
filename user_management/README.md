# User management system

Consists:
- Database
- API

The Database stores user information.

The API allows for:

- User registration
- Self-user deletion
- Get user information
- Update user information


## Database design

| id  | uname | full_name | email | hashed_password | active |
|-----|-------|-----------|-------|-----------------|--------|
| int | str   | str       | str   | str             | bool   |
