import re

USERNAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,20}$")
PASSWORD_RE = re.compile(r"^[A-Za-z0-9!@#$%^&*(){}\[\]\-_=+.,<>/?|~]{3,20}$")
NICKNAME_RE = re.compile(r"^[A-Za-z0-9!@#$%^&*(){}\[\]\-_=+.,<>/?|~]{3,20}$")

def validate_username(username: str) -> bool:
    if not username:
        return False
    return USERNAME_RE.fullmatch(username) is not None

def validate_password(password: str) -> bool:
    if not password:
        return False
    return PASSWORD_RE.fullmatch(password) is not None

def validate_nickname(nickname: str) -> bool:
    if not nickname:
        return False
    return NICKNAME_RE.fullmatch(nickname) is not None