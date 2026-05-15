import sqlite3
from models import User
from database import get_db_connection, hash_password

class AuthManager:
    @staticmethod
    def authenticate(login: str, password: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, login, full_name, role FROM users WHERE login = ? AND password_hash = ?",
            (login, hash_password(password))
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], login=row[1], full_name=row[2], role=row[3])
        return None