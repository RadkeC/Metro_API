from passlib.context import CryptContext
from fastapi import HTTPException, status

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return password_context.hash(password)


def verify_password(password, correct_password):
    """password is not hashed and correct_password is hashed"""
    return password_context.verify(password, correct_password)


def is_admin(user):
    if not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Logged user has not permission to perform that action")
