def validate_input(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3 or len(password) < 6:
        return False, "Username must be at least 3 characters and password must be at least 6 characters."
    return True, None

def authenticate(username, password):
    if username == "admin" and password == "password123":
        return True
    else:
        return False