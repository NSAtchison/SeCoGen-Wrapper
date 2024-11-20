import getpass
import hashlib
import os

def get_hashed_password(password):
    salt = os.urandom(16)  # Generate a random salt
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt, hashed_password

def check_password(password, salt, hashed_password):
    salted_password = salt + password.encode('utf-8')
    new_hashed_password = hashlib.sha256(salted_password).hexdigest()
    return new_hashed_password == hashed_password

# Sample usage (replace with secure password storage)
users = {
    "user1": (b'\x08\x1a\x07\x16\x12\x1d\x9d\x9f\x01\xc1\x96\x05\x16\x00\x1b\x0e', '2c26b46b68ffc68ff99b453c1d304cf92fd1f497971a0dba9789e7582b655393')
}


username = input("Username: ")
password = getpass.getpass("Password: ")

if username in users:
    salt, stored_hashed_password = users[username]
    if check_password(password, salt, stored_hashed_password):
        print("Login successful!")
    else:
        print("Incorrect password.")
else:
    print("User not found.")

