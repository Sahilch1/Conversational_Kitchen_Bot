import sqlite3
import hashlib

DB_NAME = "users.db"

def create_usertable():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Use a consistent table name: userstable
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_userdata(username, password_hashed):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password_hashed))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute('SELECT * FROM userstable WHERE username=? AND password=?', (username, hashed_pw))
    data = c.fetchall()
    conn.close()
    return bool(data)

def check_user_exists(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT username FROM userstable WHERE username=?', (username,))
    data = c.fetchall()
    conn.close()
    return bool(data)
