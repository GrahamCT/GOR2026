from passlib.context import CryptContext

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_pw(pw: str) -> str:
    return pwd.hash(pw)

def check_pw(pw: str, pw_hash: str) -> bool:
    return pwd.verify(pw, pw_hash)


