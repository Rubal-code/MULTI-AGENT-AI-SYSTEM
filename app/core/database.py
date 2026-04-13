import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    title TEXT,
    user_input TEXT,
    response TEXT
)
""")

conn.commit()

def save_chat(session_id, title, user_input, response):
    cursor.execute(
        "INSERT INTO chats (session_id, title, user_input, response) VALUES (?, ?, ?, ?)",
        (session_id, title, user_input, response)
    )
    conn.commit()

def get_chats(session_id):
    cursor.execute(
        "SELECT user_input, response FROM chats WHERE session_id=?",
        (session_id,)
    )
    return cursor.fetchall()

def get_all_sessions():
    cursor.execute("""
        SELECT session_id, title 
        FROM chats 
        GROUP BY session_id
    """)
    return cursor.fetchall()

def rename_chat(session_id, new_title):
    cursor.execute(
        "UPDATE chats SET title=? WHERE session_id=?",
        (new_title, session_id)
    )
    conn.commit()