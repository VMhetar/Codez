Here is the modified code with input validation and error handling:

```python
from typing import Tuple, Optional

def login(username: str, password: str) -> Optional[str]:
    if not username or not password:
        return "Username and password required"

    try:
        if username == "admin" and password == "123":
            return "Welcome"
        else:
            return "Invalid"
    except Exception as e:
        print(f"Error occurred during login: {e}")
        return None
```

Explanation:
1. I added type hints to the function parameters and return type using the `Tuple[str, str]` and `Optional[str]` types from the `typing` module.
2. The function first checks if either the `username` or `password` is empty. If either is empty, it returns the error message "Username and password required".
3. The function then tries to perform the login logic. If the username and password match the expected values, it returns "Welcome". If they don't match, it returns "Invalid".
4. If any exception occurs during the login process, the function catches the exception, prints an error message, and returns `None` to indicate an error.