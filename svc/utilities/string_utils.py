import random
import string


def generate_password(password_length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(password_length))
