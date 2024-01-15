import datetime
import mysql.connector
from mysql.connector import Error
from config import DB_NAME, DB_USER, DB_PASS


def create_db_connection():
    """
    Create connection to local database
    """
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1", database=DB_NAME, user=DB_USER, password=DB_PASS
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)


def store_token(token):
    """
    Store generated token in database with 1 hour expiry time
    """
    try:
        connection = create_db_connection()
        if connection:
            cursor = connection.cursor()
            expiry_time = (
                datetime.datetime.now() + datetime.timedelta(hours=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
            query = "INSERT INTO api_tokens (token, expires_at) VALUES (%s, %s)"
            cursor.execute(query, (token, expiry_time))
            connection.commit()
            cursor.close()
            connection.close()
    except Error as e:
        print("Error occured during storing the token:", e)


def is_token_valid(token):
    """
    Checking if token from request is in database
    """
    try:
        connection = create_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "SELECT expires_at FROM api_tokens WHERE token = %s"
            cursor.execute(query, (token,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()

            if row and row[0] > datetime.datetime.now():
                return True
        return False
    except Error as e:
        print("Error occured during token validation:", e)
