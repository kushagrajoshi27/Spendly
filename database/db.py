import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "spendly.db"


def get_db():
    """Open a connection to the SQLite database with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """Insert demo user and sample expenses if not already present."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert demo user
    demo_password_hash = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", demo_password_hash)
    )

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",))
    demo_user_id = cursor.fetchone()[0]

    # Insert 8 sample expenses across different categories
    sample_expenses = [
        (demo_user_id, 85.50, "Food", "2026-04-01", "Grocery shopping"),
        (demo_user_id, 42.00, "Food", "2026-04-03", "Restaurant dinner"),
        (demo_user_id, 35.00, "Transport", "2026-04-05", "Gas refill"),
        (demo_user_id, 120.00, "Bills", "2026-04-10", "Electricity bill"),
        (demo_user_id, 25.99, "Health", "2026-04-12", "Pharmacy"),
        (demo_user_id, 55.00, "Entertainment", "2026-04-15", "Movie tickets"),
        (demo_user_id, 89.99, "Shopping", "2026-04-20", "New shoes"),
        (demo_user_id, 15.00, "Other", "2026-04-25", "Miscellaneous"),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )

    conn.commit()
    conn.close()
