import sqlite3


conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    role TEXT
)
""")
conn.commit()


def add_user(user_id, username):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, username, "user")
        )
        conn.commit()


def get_role(user_id):
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "user"


def set_role(user_id, role):
    cursor.execute(
        "UPDATE users SET role = ? WHERE user_id = ?",
        (role, user_id)
    )
    conn.commit()


def get_user_by_username(username):
    cursor.execute(
        "SELECT user_id FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    return result[0] if result else None