{
  "code": "from typing import Tuple

def login(username: str, password: str) -> str:
    if not username or not password:
        return \"Username and password required\"
    try:
        if username == \"admin\" and password == \"123\":
            return \"Welcome\"
        else:
            return \"Invalid\"
    except Exception as e:
        return \"Error: \" + str(e)
"
}