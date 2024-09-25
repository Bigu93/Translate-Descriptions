import mysql.connector
import secrets
from mysql.connector import Error
from flask import request, jsonify, Blueprint
from datetime import datetime, timedelta
from logging_config import get_logger
from functools import wraps
from config import DB_NAME, DB_USER, DB_PASS

logger = get_logger(__name__)
auth_bp = Blueprint("auth", __name__)


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


def is_token_valid(token):
    """
    Checking if token from request is in database and not expired.
    """
    query = "SELECT expires_at FROM bearer WHERE token = %s AND expires_at > NOW()"
    result = execute_query(query, (token,))
    return bool(result)


def require_auth_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        try:
            auth_type, token = auth_header.split(None, 1)
        except ValueError:
            return jsonify({"error": "Invalid authorization header format"}), 401

        if auth_type.lower() != "bearer":
            return jsonify(
                {"error": "Authorization header must start with Bearer"}
            ), 401

        if not is_token_valid(token):
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/generate_auth_token", methods=["POST"])
def generate_auth_token():
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)
    expiry_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")

    query = "INSERT INTO bearer (token, expires_at) VALUES (%s, %s)"
    result = execute_query(query, (token, expiry_str), fetch=False)

    if result is not None:
        return jsonify({"token": token, "expires_at": expires_at.isoformat()}), 201
    else:
        return jsonify({"error": "Failed to generate token"}), 500


@auth_bp.route("/revoke_auth_token", methods=["POST"])
@require_auth_token
def revoke_auth_token():
    auth_header = request.headers.get("Authorization")
    _, token = auth_header.split(None, 1)

    query = "DELETE FROM bearer WHERE token = %s"
    result = execute_query(query, (token,), fetch=False)

    if result:
        return jsonify({"message": "Token revoked successfully"}), 200
    else:
        return jsonify({"error": "Token not found"}), 404


@auth_bp.route("/protected", methods=["GET"])
@require_auth_token
def protected_route():
    return jsonify({"message": "You have access to this protected route"}), 200
