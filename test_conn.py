from database import cursor

cursor.execute("SELECT * FROM tasks")
print(cursor.fetchall())