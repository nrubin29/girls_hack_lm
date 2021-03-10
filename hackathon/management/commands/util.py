import random
import string


def generate_password():
    """Generates a random password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
