import sqlite3
from pathlib import Path

path = Path(__file__).resolve().parent / 'ecowatt.db'
print(path)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute('SELECT username, email, hashed_password FROM users')
rows = cur.fetchall()
print(rows)
conn.close()
