# migrate.py

"""
Database Migration Script

Handles the migration of memory entries from SQLite to PostgreSQL.
Uses the psycopg2 library to connect to PostgreSQL and transfer data.
"""

import psycopg2
from psycopg2 import sql
import sqlite3
import logging

def migrate_sqlite_to_postgresql(sqlite_db_path, postgres_config, table_name="memory_entries"):
    """
    Migrate data from SQLite to PostgreSQL.

    Args:
        sqlite_db_path (str): Path to the SQLite database file.
        postgres_config (dict): Configuration parameters for PostgreSQL connection.
        table_name (str): Name of the table to migrate.
    """
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()

        # Connect to PostgreSQL
        postgres_conn = psycopg2.connect(**postgres_config)
        postgres_cursor = postgres_conn.cursor()

        # Create table in PostgreSQL if it doesn't exist
        create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            project_name TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """).format(table=sql.Identifier(table_name))
        postgres_cursor.execute(create_table_query)
        postgres_conn.commit()
        logging.info(f"Ensured PostgreSQL table '{table_name}' exists.")

        # Fetch data from SQLite
        sqlite_cursor.execute(f"SELECT project_name, user_prompt, ai_response, timestamp FROM {table_name};")
        rows = sqlite_cursor.fetchall()

        # Insert data into PostgreSQL
        insert_query = sql.SQL("""
        INSERT INTO {table} (project_name, user_prompt, ai_response, timestamp)
        VALUES (%s, %s, %s, %s);
        """).format(table=sql.Identifier(table_name))

        for row in rows:
            postgres_cursor.execute(insert_query, row)

        postgres_conn.commit()
        logging.info(f"Successfully migrated {len(rows)} entries from SQLite to PostgreSQL.")

    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
    finally:
        # Close all connections
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("logs/migration.log"),
            logging.StreamHandler()
        ]
    )

    # Define PostgreSQL connection parameters
    postgres_config = {
        'dbname': 'ai_agent_memory',
        'user': 'your_postgres_user',
        'password': 'your_postgres_password',
        'host': 'localhost',
        'port': '5432'
    }

    # Path to the existing SQLite database
    sqlite_db_path = 'ai_agent_memory.db'

    # Perform migration
    migrate_sqlite_to_postgresql(sqlite_db_path, postgres_config, table_name="memory_entries")
