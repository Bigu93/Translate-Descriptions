import datetime
import mysql.connector
import secrets
from mysql.connector import Error
from flask import jsonify
from config import DB_NAME, DB_USER, DB_PASS


def create_db_connection():
    """
    Create connection to local database.
    """
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1", database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None


def execute_query(query, params=None):
    """
    Execute a query and handle connection management.
    """
    connection = create_db_connection()
    if not connection:
        return None

    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            return cursor.fetchall()
    except Error as e:
        print(f"Error occurred during query execution: {e}")
        return None
    finally:
        connection.close()


def store_token(token):
    """
    Store generated token in database with 1 hour expiry time.
    """
    expiry_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    query = "INSERT INTO api_tokens (token, expires_at) VALUES (%s, %s)"
    execute_query(query, (token, expiry_time))


def is_token_valid(token):
    """
    Checking if token from request is in database and not expired.
    """
    query = "SELECT expires_at FROM api_tokens WHERE token = %s AND expires_at > NOW()"
    result = execute_query(query, (token,))
    return bool(result)


def remove_expired_tokens():
    """
    Remove expired tokens from the database.
    """
    query = "DELETE FROM api_tokens WHERE expires_at <= NOW()"
    execute_query(query)


def generate_token(request):
    """
    Generate a new token and store it in the database.
    """
    if request.method != "GET":
        return jsonify({"error": f"Unsupported method {request.method}"}), 405

    token = secrets.token_hex(16)
    store_token(token)
    remove_expired_tokens()
    return jsonify({"token": token})


# Call this function when your application starts
def schedule_token_cleanup():
    """
    Schedule periodic cleanup of expired tokens.
    """
    import threading

    def cleanup():
        remove_expired_tokens()
        threading.Timer(14400, cleanup).start()  # Run every 4 hours

    cleanup()
