import re

def validate_credentials(username, password):
    # Regular expression for validating an email address
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Regular expression for validating the password
    password_regex = (
        r'^(?=.*[a-z])'       # At least one lowercase letter
        r'(?=.*[A-Z])'        # At least one uppercase letter
        r'(?=.*\d.*\d)'       # At least two digits
        r'(?=.*[@$!%*?&])'    # At least one special character
        r'[A-Za-z\d@$!%*?&]{12,}$' # At least 12 characters
    )
    
    is_username_valid = re.match(email_regex, username) is not None
    is_password_valid = re.match(password_regex, password) is not None
    
    return is_username_valid and is_password_valid

# Example usage
username = 'example@example.com'
password = 'Password123!'
print(validate_credentials(username, password))  # Output: True or False
