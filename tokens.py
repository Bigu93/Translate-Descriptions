import datetime
import mysql.connector
import secrets
from mysql.connector import Error
from flask import jsonify
from config import DB_NAME, DB_USER, DB_PASS
from utils import get_logger

logger = get_logger("app")


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
        logger.error(f"Error while connecting to MySQL: {e}")
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
        logger.error(f"Error occurred during query execution: {e}")
        return None
    finally:
        connection.close()


def remove_expired_tokens():
    """
    Remove expired tokens from the database and log the number of removed tokens.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "DELETE FROM api_tokens WHERE expires_at <= %s"
    result = execute_query(query, (current_time,))

    if result is not None:
        affected_rows = result[0][0] if result else 0
        logger.info(f"Removed {affected_rows} expired tokens at {current_time}")
    else:
        logger.error("Failed to remove expired tokens")


def generate_token(request):
    if request.method != "GET":
        return jsonify({"error": f"Unsupported method {request.method}"}), 405

    token = secrets.token_hex(16)
    expiry_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    query = "INSERT INTO api_tokens (token, expires_at) VALUES (%s, %s)"
    execute_query(query, (token, expiry_time))

    remove_expired_tokens()  # Clean up expired tokens after generating a new one
    logger.info(f"Generated new token: {token}, expires at: {expiry_time}")
    return jsonify({"token": token})


def is_token_valid(token):
    """
    Checking if token from request is in database and not expired.
    """
    query = "SELECT expires_at FROM api_tokens WHERE token = %s AND expires_at > NOW()"
    result = execute_query(query, (token,))
    return bool(result)


# Function to manually check and log all tokens
def check_all_tokens():
    query = "SELECT token, expires_at FROM api_tokens ORDER BY expires_at"
    results = execute_query(query)
    if results:
        for token, expires_at in results:
            logger.info(f"Token: {token}, Expires at: {expires_at}")
    else:
        logger.info("No tokens found in the database.")
