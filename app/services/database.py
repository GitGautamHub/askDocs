# app/services/database.py
import os
import sqlite3

DB_PATH = "data/ingestion_status.db"


# get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# delete a file entry
def delete_file_entry(file_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM file_status WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()

# setup the database
def setup_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file_status (
            file_id TEXT PRIMARY KEY,
            file_name TEXT,
            status TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()

# update a file entry
def update_file_status(file_id: str, file_name: str, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO file_status (file_id, file_name, status) VALUES (?, ?, ?)",
        (file_id, file_name, status),
    )
    conn.commit()
    conn.close()

# get the status of a file
def get_file_status(file_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM file_status WHERE file_id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()
    return result["status"] if result else None

# get all documents
def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_name, status FROM file_status")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row['file_id'], "name": row['file_name'], "status": row['status']} for row in rows]