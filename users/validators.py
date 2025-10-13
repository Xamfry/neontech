import hashlib
import requests

class PwnedPasswordValidator:
    def validate(self, password, user=None):
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        r = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if r.ok and any(line.split(':')[0] == suffix for line in r.text.splitlines()):
            from django.core.exceptions import ValidationError
            raise ValidationError('Пароль обнаружен в публичных утечках. Выберите другой.')
    def get_help_text(self):
        return 'Проверка пароля на утечки через HIBP.'
