from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")


def hash(password: str):
    return password_hash.hash(password)

def verify(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)