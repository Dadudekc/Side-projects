# modules/db_manager.py

import sqlite3
import json

DB_NAME = "analysis_results.db"

def get_connection(db_path=DB_NAME):
    """
    Establishes and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    return conn

def initialize_db(conn):
    """
    Creates the 'analysis_files' table if it does not already exist.
    """
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_path TEXT,
            analyzed_at TEXT,
            description TEXT,
            imports TEXT,
            classes TEXT,
            functions TEXT,
            constants TEXT,
            api_calls TEXT
        )
    ''')
    conn.commit()

def insert_file_analysis(conn, file_details):
    """
    Inserts the analysis details for a single file into the database.
    """
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_files (
            file_name, file_path, analyzed_at, description, imports, classes, functions, constants, api_calls
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_details.get("file"),
        file_details.get("path"),
        file_details.get("analyzed_at"),
        file_details.get("description"),
        json.dumps(file_details.get("imports")),
        json.dumps(file_details.get("classes")),
        json.dumps(file_details.get("functions")),
        json.dumps(file_details.get("constants")),
        json.dumps(file_details.get("api_calls"))
    ))
    conn.commit()

def insert_project_summary(conn, summary):
    """
    Inserts the entire project's file analysis results into the database.
    """
    for file_detail in summary.get("files", []):
        insert_file_analysis(conn, file_detail)
