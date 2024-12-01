import hashlib
import getpass
import json

# Simulate a database -  IN A REAL APPLICATION, USE A SECURE DATABASE!
try:
    with open("users.json", "r") as f:
        user_database = json.load(f)
except FileNotFoundError:
    user_database = {}


def check_password(username, password):
    if username in user_database:
        stored_hash = user_database[username]
        # Hash the provided password using the same algorithm
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password == stored_hash
    return False


def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if check_password(username, password):
        print("Login successful!")
    else:
        print("Invalid username or password.")


def register():
  username = input("Username: ")
  if username in user_database:
    print("Username already exists. Please choose a different one.")
    return
  password = getpass.getpass("Password: ")
  hashed_password = hashlib.sha256(password.encode()).hexdigest()
  user_database[username] = hashed_password
  with open("users.json", "w") as f:
      json.dump(user_database, f)
  print("Registration successful!")


if __name__ == "__main__":
    action = input("Login or Register? (login/register): ")
    if action.lower() == "login":
        login()
    elif action.lower() == "register":
        register()
    else:
        print("Invalid action.")

