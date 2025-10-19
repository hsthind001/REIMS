import sqlite3

conn = sqlite3.connect('backend/reims.db')
cursor = conn.cursor()

# Get table structure
cursor.execute('PRAGMA table_info(properties)')
columns = cursor.fetchall()
print('Properties table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print('\n')

# Get data
cursor.execute('SELECT * FROM properties')
properties = cursor.fetchall()
print(f'Properties count: {len(properties)}')

for i, prop in enumerate(properties):
    print(f'\nProperty {i+1}:')
    for j in range(len(columns)):
        print(f'  {columns[j][1]}: {prop[j]}')

conn.close()

