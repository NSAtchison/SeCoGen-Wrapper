import ssl
import socket
import snmp_client
import mysql.connector
import hashlib
import jwt

# --- Configuration ---
SQL_HOST = "localhost"
SQL_USER = "your_db_user"
SQL_PASSWORD = "your_db_password"
SQL_DATABASE = "your_db_name"
SSL_CERT_FILE = "server.crt"  # Path to your SSL certificate
SSL_KEY_FILE = "server.key"  # Path to your SSL key
SNMP_COMMUNITY = "your_snmp_community"
SNMP_HOST = "your_snmp_host"
SNMP_OID = ".1.3.6.1.2.1.1.5.0" # Example OID, replace with your actual OID


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


def add_user(username, password):
    """Adds a new user to the database."""
    mydb = mysql.connector.connect(
        host=SQL_HOST, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE
    )
    cursor = mydb.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Secure hashing
    try:
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
    """Authenticates a user against the database."""
    mydb = mysql.connector.connect(
        host=SQL_HOST, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE
    )
    cursor = mydb.cursor()
    try:
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
        mydb.close()
        return False


# --- SSL Functions ---
def create_ssl_socket():

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=SSL_CERT_FILE, keyfile=SSL_KEY_FILE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(sock, server_side=True)
    return ssl_socket


# --- SNMP Functions ---
def get_snmp_data(ip, community, oid):

    try:
        data = snmp_client.get(ip, community, oid)
        return data
    except Exception as e:
        print(f"SNMP request failed: {e}")
        return None


# --- JWT (JSON Web Token) for Secure Session Management ---
def generate_jwt(username):
    """Generates a JWT for the authenticated user."""
    payload = {"username": username}
    secret_key = "your_secret_key" # KEEP THIS SECRET!  Replace with a strong, randomly generated key.
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_jwt(token, secret_key):
    """Verifies the JWT and returns the payload if valid, otherwise None."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
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
        username, password = data.split(":")  # Expect username:password

        if authenticate_user(username, password):
            # Successful authentication
            jwt_token = generate_jwt(username)
            conn.sendall(jwt_token.encode())

            # Get SNMP data (example) - replace with your logic as needed
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
        ssl_socket.close()


if __name__ == "__main__":
    init_db()
    ssl_socket = create_ssl_socket()
    ssl_socket.bind(("", 443))  # Bind to port 443 for HTTPS
    ssl_socket.listen(5)  # Listen for up to 5 clients

    print("Server listening on port 443...")
    while True:
        handle_client(ssl_socket)

