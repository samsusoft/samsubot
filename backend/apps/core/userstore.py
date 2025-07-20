from apps.core.auth import get_password_hash

fake_user = {
    "username": "admin",
    "hashed_password": get_password_hash("admin123")
}