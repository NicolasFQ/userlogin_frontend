import oracledb
import os
from passlib.hash import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any

# Database configuration
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'your_username'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'dsn': os.getenv('DB_DSN', 'localhost:1521/your_service_name')
}

def get_connection():
    """Create and return a database connection"""
    try:
        connection = oracledb.connect(**DB_CONFIG)
        return connection
    except oracledb.Error as error:
        print(f"Error connecting to database: {error}")
        raise

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.verify(password, hashed)

class UserDB:
    @staticmethod
    def create_user(email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
        """Create a new user in the database"""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                password_hash = hash_password(password)
                
                sql = """
                INSERT INTO users (email, password_hash, full_name)
                VALUES (:1, :2, :3)
                RETURNING user_id, email, full_name, created_at INTO :4, :5, :6, :7
                """
                
                user_id = cursor.var(int)
                email_out = cursor.var(str)
                full_name_out = cursor.var(str)
                created_at = cursor.var(datetime)
                
                cursor.execute(sql, (email, password_hash, full_name, 
                                   user_id, email_out, full_name_out, created_at))
                connection.commit()
                
                return {
                    'user_id': user_id.getvalue()[0],
                    'email': email_out.getvalue()[0],
                    'full_name': full_name_out.getvalue()[0],
                    'created_at': created_at.getvalue()[0]
                }
        except oracledb.Error as error:
            print(f"Error creating user: {error}")
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT user_id, email, password_hash, full_name, created_at, last_login, is_active
                    FROM users
                    WHERE email = :1
                """, (email,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'email': row[1],
                        'password_hash': row[2],
                        'full_name': row[3],
                        'created_at': row[4],
                        'last_login': row[5],
                        'is_active': bool(row[6])
                    }
                return None
        except oracledb.Error as error:
            print(f"Error getting user: {error}")
            return None

    @staticmethod
    def update_last_login(user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = :1
                """, (user_id,))
                connection.commit()
                return True
        except oracledb.Error as error:
            print(f"Error updating last login: {error}")
            return False

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        user = UserDB.get_user_by_email(email)
        if user and verify_password(password, user['password_hash']):
            UserDB.update_last_login(user['user_id'])
            # Remove password_hash from returned user data
            user.pop('password_hash', None)
            return user
        return None 