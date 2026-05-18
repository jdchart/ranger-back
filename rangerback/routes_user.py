from fastapi import APIRouter, Form, HTTPException, Header
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from .database import db
import os
from dotenv import load_dotenv

router = APIRouter()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_auth_token(username):
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

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

@router.post("/users/create")
def create_user(email: str = Form(...), username: str = Form(...), password: str = Form(...)):
    exists = db.does_entry_exist(
        "users",
        "username",
        username
    )

    if exists:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    password_hash = pwd_context.hash(password)
    user_id = db.create_entry(
        "users",
        {
            "username" : username,
            "email" : email,
            "password_hash" : password_hash,
            "admin" :  False,
            "thumbnail_url" : None,
            "validated" : False
        }
    )

    return {
        "message": "User created",
        "user_id": user_id[0]
    }

@router.post("/users/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = db.get_entry(
        "users",
        "username",
        username
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    valid = pwd_context.verify(
        password,
        user["password_hash"]
    )

    if not valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_auth_token(username)

    return {
        "message": "Login successful",
        "access_token": token
    }

@router.post("/users/get-profile")
def get_me(
    authorization: str = Header(None)
):
    user = get_authenticated_user(
        authorization
    )

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "admin" : user["admin"],
        "thumbnail_url" : user["thumbnail_url"],
        "validated" : user["validated"]
    }

@router.post("/users/me")
def get_me(
    authorization: str = Header(None),
    msg: str = Form(...)
):
    user = get_authenticated_user(
        authorization
    )

    # Authorized from here
    print(msg)

    return {
        "id": user["id"],
        "username": user["username"]
    }