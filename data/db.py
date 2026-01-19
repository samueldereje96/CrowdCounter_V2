import sqlite3

DB_PATH = "data\occupancy.db"

def log_to_db(current_count, avg_occupancy, max_occupancy, temperature=25.0, limit_exceeded=False):
    """
    Log occupancy + temperature + limit_exceeded to SQLite.
    temperature is simulated for now.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS occupancy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            current_count INTEGER,
            avg_occupancy REAL,
            max_occupancy INTEGER,
            temperature REAL,
            limit_exceeded INTEGER
        )
    """)
    
    # Insert new log
    cursor.execute("""
        INSERT INTO occupancy_logs (timestamp, current_count, avg_occupancy, max_occupancy, temperature, limit_exceeded)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
    """, (current_count, avg_occupancy, max_occupancy, temperature, int(limit_exceeded)))
    
    conn.commit()
    conn.close()
