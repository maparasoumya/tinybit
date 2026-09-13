import secrets
import string

from .models import ShortURL


BASE62 = string.ascii_letters + string.digits


def generate_short_code(length=6):
    return "".join(secrets.choice(BASE62) for _ in range(length))


def generate_unique_short_code(length=6):
    while True:
        code = generate_short_code(length)

        if not ShortURL.objects.filter(short_code=code).exists():
            return code