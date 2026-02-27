Here's the modified code with the requested changes:

```python
from typing import Tuple

def login(username: str, password: str) -> Tuple[str, int]:
    if not username or not password:
        return "Username and password required", 400

    try:
        if username == "admin" and password == "123":
            return "Welcome", 200
        else:
            return "Invalid", 401
    except Exception as e:
        return f"Error: {str(e)}", 500
```

Explanation:

1. Added type hints for the function parameters and return value using the `Tuple[str, int]` type. This indicates that the function returns a tuple with a string and an integer.
2. Added input validation to check if the `username` or `password` is empty. If either of them is empty, the function returns the string "Username and password required" and the HTTP status code 400 (Bad Request).
3. Added a `try-except` block to handle any potential exceptions that may occur during the login process. If an exception is raised, the function returns an error message with the HTTP status code 500 (Internal Server Error).
4. If the username and password are valid, the function returns the string "Welcome" and the HTTP status code 200 (OK).
5. If the username and password are invalid, the function returns the string "Invalid" and the HTTP status code 401 (Unauthorized).

The function now provides input validation, error handling, and type hints, making it more robust and easier to maintain.