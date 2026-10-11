"""
init_db.py – Standalone script to create database tables.

Run once after creating the MySQL database:
    python init_db.py

The script reads DB credentials from .env.
"""

from backend.database import init_db, check_connection

if __name__ == "__main__":
    if not check_connection():
        print(
            "ERROR: Cannot connect to the database.\n"
            "Check DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD in your .env file."
        )
        raise SystemExit(1)

    init_db()
    print("Database tables created successfully.")
