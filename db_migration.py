import sqlite3
import shutil
import logging
from datetime import datetime

# Configure the logger
log_file = f"migration_{datetime.now().strftime('%Y%m%d')}_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

def apply_migration(old_database, new_database):
    try:
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
            VALUES (?, ?, ?, ?, ?)
        ''', rows)

        # Commit changes in the new database
        new_connection.commit()
        
        # Log success message
        logging.info("Migration applied successfully.")

    except sqlite3.Error as e:
        # Log error message
        logging.error(f"Error applying migration: {str(e)}")
    finally:
        # Close connections
        old_connection.close()
        new_connection.close()

if __name__ == "__main__":
    # Specify the paths for old and new databases
    old_database_file = "website_checker_old.db"
    new_database_file = "website_checker.db"

    # Append current date to the old database file for backup
    current_date = datetime.now().strftime("%Y%m%d")
    backup_file = f"website_checker_backup_{current_date}.db"

    try:
        # Backup the old database
        shutil.copy(old_database_file, backup_file)

        # Apply the migration
        apply_migration(old_database_file, new_database_file)

    except Exception as e:
        # Log any other errors
        logging.error(f"An error occurred: {str(e)}")
