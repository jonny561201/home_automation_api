import secrets
import string


def generate_password(password_length):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(password_length))
