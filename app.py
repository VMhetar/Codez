def login(username: str, password: str) -> str:
    if not username or not password:
        return "Username and password required"
    if username == "admin" and password == "123":
        return "Welcome"
    return "Invalid"
