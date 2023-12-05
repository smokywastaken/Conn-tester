import os
import requests
import configparser
import logging
import sqlite3
from datetime import datetime

CURRENT_PATH =os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CURRENT_PATH, "config.ini")
DATABASE_FILE= os.path.join(CURRENT_PATH, "website_checker.db")

def initialize_database():#Creates a database for app
    connection = sqlite3.connect(os.path.join(CURRENT_PATH, DATABASE_FILE))
    cursor = connection.cursor()

    # Create table if its not there
    cursor.execute('''CREATE TABLE IF NOT EXISTS website_status (id INTEGER PRIMARY KEY AUTOINCREMENT,time TEXT,date TEXT,website TEXT,
                   availability_status TEXT,status_code INTEGER)''')

    connection.commit()

    connection.close()

def insert_into_database(time, date, website, availability_status, status_code):
    connection = sqlite3.connect(os.path.join(CURRENT_PATH, DATABASE_FILE))
    cursor = connection.cursor()

    # Insert a new record
    cursor.execute('''
        INSERT INTO website_status (time, date, website, availability_status, status_code)
        VALUES (?, ?, ?, ?, ?)
    ''', (time, date, website, availability_status, status_code))

    connection.commit()
    connection.close()

def check_website_availability(websites):
    current_datetime = datetime.now()

    for name, url in websites.items():
        try:
            response = requests.get(url)
            if response.status_code >= 200 and response.status_code < 300:
                availability_status = "reachable"
            else:
                availability_status = "unreachable"
            
            print(f"{name}: {url} is {availability_status}. Status Code: {response.status_code}")

            # Insert the result into the database
            insert_into_database(
                time=current_datetime.strftime("%H:%M:%S"),
                date=current_datetime.strftime("%Y-%m-%d"),
                website=url,
                availability_status=availability_status,
                status_code=response.status_code
            )
        except requests.ConnectionError:
            print(f"{name}: {url} is unreachable. Connection Error.")
            # Insert the result into the database with status code -1 for connection error
            insert_into_database(
                time=current_datetime.strftime("%H:%M:%S"),
                date=current_datetime.strftime("%Y-%m-%d"),
                website=url,
                availability_status="unreachable",
                status_code=-1
            )
        except requests.RequestException as e:
            print(f"{name}: {url} is unreachable. {str(e)}")
            # Insert the result into the database with status code -1 for other errors
            insert_into_database(
                time=current_datetime.strftime("%H:%M:%S"),
                date=current_datetime.strftime("%Y-%m-%d"),
                website=url,
                availability_status="unreachable",
                status_code=-1
            )
            logging.error(f"Failed to reach {name}: {url}. Error: {str(e)}")

def read_config(file_path=CONFIG_FILE):
    config = configparser.ConfigParser()
    current_datetime = datetime.now()
    try:
        config.read(file_path)
        websites =config["WEBSITES"]
        return websites
    except KeyError:
        logging.error(f"[{current_datetime}]Config file {file_path} is empty or missing 'WEBSITES' section.")
        return {}
    except FileNotFoundError:
        logging.error(f"[{current_datetime}]Config file {file_path} not found.")
        return {}

if __name__ == "__main__":
    # Configure logging to write to a file
    logging.basicConfig(filename=os.path.join(CURRENT_PATH, 'website_checker.log'), level=logging.ERROR)

    # Initialize the database
    initialize_database()


    websites_to_check = read_config(CONFIG_FILE)
    
    if websites_to_check:
        check_website_availability(websites_to_check)
    else:
        print("No websites to check. Please ensure the config file is properly configured.")
