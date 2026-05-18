from fastapi import HTTPException, Header
from jose import jwt, JWTError
from .database import db
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_authenticated_user(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    try:
        token = authorization.split(" ")[1]

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("username")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = db.get_entry(
            "users",
            "username",
            username
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )