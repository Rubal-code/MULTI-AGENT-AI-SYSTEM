import sqlite3

conn=sqlite3.connect("chat.db",check_same_thread=False) # check_same_thread means that multiple users can interact with database without any streamlit app crash because of multiple threads trying to access the database at the same time. It allows the connection to be shared across different threads.
cursor=conn.cursor()

# create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        user_input TEXT,
        response   TEXT
    )
''')

conn.commit()

def save_chat(session_id,user_input,response):
    cursor.execute(
        "INSERT INTO chats (session_id, user_input, response) VALUES (?, ?, ?)",
        (session_id, user_input, response)
    )
    conn.commit()

def get_chats(session_id):
    cursor.execute(
        "SELECT user_input, response FROM chats WHERE session_id = ?",
        (session_id,)
    )
    return cursor.fetchall()

def get_all_sessions():
    cursor.execute("SELECT DISTINCT session_id FROM chats")
    return [row[0] for row in cursor.fetchall()]