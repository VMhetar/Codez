def authenticate_user(username, password):
    # Load user credentials from a secure storage
    stored_username = "myuser"
    stored_password = "mypassword"
    
    if username == stored_username and password == stored_password:
        return True
    else:
        return False