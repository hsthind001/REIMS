import sqlite3
conn = sqlite3.connect('reims.db')
cur = conn.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [t[0] for t in cur.fetchall()]
print("Tables in database:", tables)
print("\nStores table exists:", 'stores' in tables)
conn.close()

