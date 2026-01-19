import sqlite3

# Connect to your database
conn = sqlite3.connect("data/occupancy.db")  # adjust path if needed
cursor = conn.cursor()

# 1️⃣ List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", tables)

# 2️⃣ Check columns of the occupancy_logs table
cursor.execute("PRAGMA table_info(occupancy_logs);")
columns = cursor.fetchall()
print("Columns in occupancy_logs:", columns)

# 3️⃣ Check first few rows to see logged data
cursor.execute("SELECT * FROM occupancy_logs LIMIT 5;")
rows = cursor.fetchall()
print("First 5 rows:", rows)

# Close the connection
conn.close()
