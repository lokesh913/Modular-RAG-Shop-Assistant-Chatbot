# import library
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# read csv file (resolve path relative to this script's directory)
csv_file = os.path.join(os.path.dirname(__file__), 'shop-product-catalog.csv')
data = pd.read_csv(csv_file)

# connect to MySQL
db_connection = mysql.connector.connect(
    host=os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost")),
    user=os.getenv("MYSQLUSER", os.getenv("DB_USER", "root")),
    password=os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD")),
    database=os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "assistant_chatbot")),
    port=int(os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306")))
)

cursor = db_connection.cursor()


for index, row in data.iterrows():
    sql = """
    INSERT INTO products (ProductID,ProductName,ProductBrand,Gender,Price,Description,PrimaryColor)
    VALUES (%s, %s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, tuple(row))

db_connection.commit()


cursor.close()
db_connection.close()
