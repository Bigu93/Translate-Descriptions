import datetime
import mysql.connector
from mysql.connector import Error


def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost", database="", user="", password=""
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)


def store_token(token):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        expiry_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        query = "INSERT INTO api_tokens (token, expires_at) VALUES (%s, %s)"
        cursor.execute(query, (token, expiry_time))
        connection.commit()
        cursor.close()
        connection.close()


def is_token_valid(token):
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
