import datetime
import mysql.connector
import secrets
from mysql.connector import Error
from flask import jsonify, Blueprint
from config import DB_NAME, DB_USER, DB_PASS
from utils import get_logger

logger = get_logger("app")
token_bp = Blueprint("token", __name__)


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


def execute_query(query, params=None, fetch=True):
    """
    Execute a query and handle connection management.
    """
    connection = create_db_connection()
    if not connection:
        return None
    try:
        with connection.cursor(buffered=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            if fetch:
                return cursor.fetchall()
            else:
                return cursor.rowcount
    except Error as e:
        logger.error(f"Error occurred during query execution: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()


@token_bp.route("/generate", methods=["GET"])
def generate_token():
    token = secrets.token_hex(16)
    expiry_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    query = "INSERT INTO api_tokens (token, expires_at) VALUES (%s, %s)"
    result = execute_query(query, (token, expiry_time), fetch=False)
    if result is not None:
        logger.info(f"Generated new token: {token}, expires at: {expiry_time}")
        return jsonify({"token": token})
    else:
        logger.error("Failed to generate token")
        return jsonify({"error": "Failed to generate token"}), 500


@token_bp.route("/cleanup", methods=["POST"])
def cleanup_tokens():
    """
    Remove expired tokens from the database and log the number of removed tokens.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "DELETE FROM api_tokens WHERE expires_at <= %s"
    affected_rows = execute_query(query, (current_time,), fetch=False)
    if affected_rows is not None:
        logger.info(f"Removed {affected_rows} expired tokens at {current_time}")
        return jsonify({"message": f"Removed {affected_rows} expired tokens"}), 200
    else:
        logger.error("Failed to remove expired tokens")
        return jsonify({"error": "Failed to remove expired tokens"}), 500


def is_token_valid(token):
    """
    Checking if token from request is in database and not expired.
    """
    query = "SELECT expires_at FROM api_tokens WHERE token = %s AND expires_at > NOW()"
    result = execute_query(query, (token,))
    return bool(result)


def obfuscate_token(token):
    """Obfuscate the token by showing only the first and last few characters."""
    if len(token) <= 8:
        # If the token is very short, just return it as is (or decide on a different approach)
        return "XD"
    return f"{token[:1]}****{token[-1:]}"


# Function to manually check and log all tokens
@token_bp.route("/check", methods=["GET"])
def check_all_tokens():
    query = "SELECT token, expires_at FROM api_tokens ORDER BY expires_at"
    results = execute_query(query)
    if results:
        tokens = [
            {
                "token": obfuscate_token(token),
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for token, expires_at in results
        ]
        logger.info(f"Found {len(tokens)} tokens in the database")
        return jsonify(tokens), 200
    elif results is None:
        logger.error("Error occurred while fetching tokens")
        return jsonify({"error": "Error occurred while fetching tokens"}), 500
    else:
        logger.info("No tokens found in the database.")
        return jsonify({"message": "No tokens found in the database"}), 200


@token_bp.route("/check_setup", methods=["GET"])
def check_database_setup():
    connection = create_db_connection()
    if not connection:
        logger.error("Failed to connect to the database")
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        with connection.cursor(buffered=True) as cursor:
            # Check if the table exists
            cursor.execute("SHOW TABLES LIKE 'api_tokens'")
            if not cursor.fetchone():
                logger.error("The api_tokens table does not exist")
                return jsonify({"error": "The api_tokens table does not exist"}), 500

            # Check table structure
            cursor.execute("DESCRIBE api_tokens")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]
            if "token" not in column_names or "expires_at" not in column_names:
                logger.error("The api_tokens table structure is incorrect")
                return jsonify(
                    {"error": "The api_tokens table structure is incorrect"}
                ), 500

        logger.info("Database setup appears to be correct")
        return jsonify({"message": "Database setup appears to be correct"}), 200
    except Error as e:
        logger.error(f"Error checking database setup: {e}")
        return jsonify({"error": f"Error checking database setup: {str(e)}"}), 500
    finally:
        if connection.is_connected():
            connection.close()
