# backend/apps/core/userstore.py
# User store for managing user data and authentication
from typing import Optional, Dict, Any
from apps.core.security import get_password_hash  # ✅ import from security.py

_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True
    },
    "admin1": {
        "username": "admin1",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True
    },
    "admin2": {
        "username": "admin2",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True
    }
}

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    return _users_db.get(username)

def create_user(username: str, password: str) -> Dict[str, Any]:
    if username in _users_db:
        raise ValueError("User already exists")
    user_data = {
        "username": username,
        "hashed_password": get_password_hash(password),
        "is_active": True
    }
    _users_db[username] = user_data
    return user_data

def update_user_password(username: str, new_password: str) -> bool:
    if username not in _users_db:
        return False
    _users_db[username]["hashed_password"] = get_password_hash(new_password)
    return True