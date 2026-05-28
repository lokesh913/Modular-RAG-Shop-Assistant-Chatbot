import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Dynamically read Railway env variables, falling back to local configurations
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD")),
        database=os.getenv("MYSQLDATABASE", "assistant_chatbot"),
        port=int(os.getenv("MYSQLPORT", "3306"))
    )