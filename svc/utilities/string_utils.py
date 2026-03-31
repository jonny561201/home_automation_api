import secrets
import string


def generate_password(password_length):
    letters = string.ascii_lowercase
    return ''.join(secrets.choice(letters) for i in range(password_length))
