import random
import string


def generate_random_password(length=10):
    """
    Генерирует случайный пароль длиной length.
    Паттерн: буквы (верхний и нижний регистр), цифры, специальные символы.
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))
