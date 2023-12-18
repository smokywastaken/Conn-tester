import sqlite3
import shutil
import logging
import os
from datetime import datetime

# Configure the logger
log_file = "migration_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

def apply_migration(old_database, new_database):
    try:
        # Create a timestamp for the backup folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a backup folder
        backup_folder = f"migrations/backup_{timestamp}"
        os.makedirs(backup_folder)

        # Backup the old database to the backup folder
        backup_file = f"{backup_folder}/{os.path.basename(old_database)}"
        shutil.copy(old_database, backup_file)

        # Connect to the old database
        old_connection = sqlite3.connect(old_database)
        old_cursor = old_connection.cursor()

        # Connect to the new database
        new_connection = sqlite3.connect(new_database)
        new_cursor = new_connection.cursor()

        # Create the new table in the new database
        new_cursor.execute('''
            CREATE TABLE IF NOT EXISTS website_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                date TEXT,
                website TEXT,
                availability_status TEXT,
                status_code INTEGER
            )
        ''')

        # Copy data from old to new database
        old_cursor.execute("SELECT * FROM website_status")
        rows = old_cursor.fetchall()
        new_cursor.executemany('''
            INSERT INTO website_status (time, date, website, availability_status, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', rows)

        # Commit changes in the new database
        new_connection.commit()

        # Log success message
        logging.info(f"Migration applied successfully. Backup saved to {backup_folder}")

    except sqlite3.Error as e:
        # Log error message
        logging.error(f"Error applying migration: {str(e)}")
    finally:
        # Close connections
        if 'old_connection' in locals():
            old_connection.close()
        if 'new_connection' in locals():
            new_connection.close()

if __name__ == "__main__":
    # Specify the paths for old and new databases
    old_database_file = "website_checker.db"
    new_database_file = "website_checker.db"

    try:
        # Apply the migration
        apply_migration(old_database_file, new_database_file)

    except Exception as e:
        # Log any other errors
        logging.error(f"An error occurred: {str(e)}")
