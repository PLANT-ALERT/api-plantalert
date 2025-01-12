import mariadb
import sys
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_database = os.getenv("DB_DATABASE")

try:
    conn = mariadb.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_database
    )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

def return_cursor():
    return cur