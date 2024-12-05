import ssl
import socket
import os
import hashlib
import jwt
from pysnmp.hlapi import *  #Import pysnmp specifically for better clarity
import mysql.connector

# --- Configuration from Environment Variables ---
SQL_HOST = os.environ.get("SQL_HOST", "localhost")
SQL_USER = os.environ.get("SQL_USER")
SQL_PASSWORD = os.environ.get("SQL_PASSWORD")
SQL_DATABASE = os.environ.get("SQL_DATABASE")
SSL_CERT_FILE = os.environ.get("SSL_CERT_FILE", "server.crt")
SSL_KEY_FILE = os.environ.get("SSL_KEY_FILE", "server.key")
SNMP_COMMUNITY = os.environ.get("SNMP_COMMUNITY")
SNMP_HOST = os.environ.get("SNMP_HOST")
SNMP_OID = os.environ.get("SNMP_OID", ".1.3.6.1.2.1.1.5.0")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


#Input validation for environment variables
required_env_vars = ["SQL_USER", "SQL_PASSWORD", "SQL_DATABASE", "SNMP_COMMUNITY", "SNMP_HOST", "JWT_SECRET_KEY"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# --- Database Functions ---
def init_db():
    """Initializes the database connection and creates the users table if it doesn't exist."""
    try:
        mydb = mysql.connector.connect(
            host=SQL_HOST, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE
        )
        cursor = mydb.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        mydb.commit()
        mydb.close()
        print("Database initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Database initialization failed: {err}")
        raise  # Re-raise the exception to halt execution


def add_user(username, password):
    """Adds a new user to the database.  Returns True on success, False otherwise."""
    try:
        mydb = mysql.connector.connect(
            host=SQL_HOST, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE
        )
        cursor = mydb.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password),
        )
        mydb.commit()
        mydb.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error adding user: {err}")
        mydb.rollback()
        mydb.close()
        return False


def authenticate_user(username, password):
    """Authenticates a user against the database. Returns True on success, False otherwise."""
    try:
        mydb = mysql.connector.connect(
            host=SQL_HOST, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE
        )
        cursor = mydb.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()
        mydb.close()
        if result:
            hashed_password = result[0]
            return hashlib.sha256(password.encode()).hexdigest() == hashed_password
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Authentication error: {err}")
        return False



# --- SSL Functions ---
def create_ssl_socket():
    """Creates an SSL socket."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=SSL_CERT_FILE, keyfile=SSL_KEY_FILE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(sock, server_side=True)
    return ssl_socket


# --- SNMP Functions ---
def get_snmp_data(ip, community, oid):
    """Retrieves SNMP data."""
    try:
        for errorIndication, errorStatus, errorIndex, varBinds in getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip, 161)),
            ObjectType(ObjectIdentity(oid)),
        ):
            if errorIndication:
                print(f"SNMP error indication: {errorIndication}")
                return None
            elif errorStatus:
                print(
                    f"SNMP error: {errorStatus} at {errorIndex}"
                )
                return None
            else:
                for varBind in varBinds:
                    return str(varBind[1])
    except Exception as e:
        print(f"SNMP request failed: {e}")
        return None


# --- JWT (JSON Web Token) for Secure Session Management ---
def generate_jwt(username):
    """Generates a JWT for the authenticated user."""
    payload = {"username": username}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt(token):
    """Verifies the JWT and returns the payload if valid, otherwise None."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# --- Main Application Logic ---
def handle_client(ssl_socket):
    """Handles a single client connection."""
    try:
        conn, addr = ssl_socket.accept()
        print(f"Accepted connection from {addr}")
        data = conn.recv(1024).decode()
        username, password = data.split(":")

        if authenticate_user(username, password):
            jwt_token = generate_jwt(username)
            conn.sendall(jwt_token.encode())

            snmp_data = get_snmp_data(SNMP_HOST, SNMP_COMMUNITY, SNMP_OID)
            if snmp_data:
                conn.sendall(snmp_data.encode())
            else:
                conn.sendall(b"Error getting SNMP data")
        else:
            conn.sendall(b"Authentication failed")
        conn.close()
    except ssl.SSLError as e:
        print(f"SSL error: {e}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close() #Ensure connection is closed even if an error occurs


if __name__ == "__main__":
    init_db()
    ssl_socket = create_ssl_socket()
    ssl_socket.bind(("", 443))
    ssl_socket.listen(5)

    print("Server listening on port 443...")
    while True:
        handle_client(ssl_socket)

