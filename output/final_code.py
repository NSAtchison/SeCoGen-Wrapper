import hashlib
import getpass
import os

def get_password_hash(filename="password.hash"):
    """Retrieves the password hash from a file.  Creates the file if it doesn't exist."""
    try:
        with open(filename, "r") as f:
            hashed_password = f.readline().strip()
            return hashed_password
    except FileNotFoundError:
        print("Password file not found. Please set a password.")
        set_password(filename)  # Call the function to create and save the password hash
        return get_password_hash(filename)  # Call the function recursively to load the newly created password hash


def set_password(filename="password.hash"):
    """Sets a new password, hashes it, and saves it to a file."""
    while True:
        password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        if password == confirm_password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()  #Uses SHA256 for hashing
            with open(filename, "w") as f:
                f.write(hashed_password)
            print("Password set successfully.")
            break
        else:
            print("Passwords do not match. Please try again.")


def check_credentials(username, password, hashed_password):
    """Checks username and password against the stored hash."""
    if username == "admin": #Still hardcodes username, this should be improved in real scenario.
        user_hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return user_hashed_password == hashed_password
    else:
        return False


def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    stored_hash = get_password_hash()
    if check_credentials(username, password, stored_hash):
        print("Login successful!")
    else:
        print("Login failed.")


if __name__ == "__main__":
    main()

