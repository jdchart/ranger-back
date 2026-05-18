from fastapi import APIRouter, Header, Form
from .database import db
from .utils import get_authenticated_user

router = APIRouter()

@router.post("/admin/get-users")
def get_users(
    authorization: str = Header(None)
):
    user = get_authenticated_user(
        authorization
    )

    if user["admin"] == True:
        users = db.list_entries("users")
        return {"users" : users}
    
@router.post("/admin/remove-user")
def remove_user(
    authorization: str = Header(None),
    user_id: int = Form(...)
):
    user = get_authenticated_user(
        authorization
    )

    if user["admin"] == True:
        db.delete_entry("users", "id", user_id)

@router.post("/admin/validate-user")
def validate_user(
    authorization: str = Header(None),
    user_id: int = Form(...)
):
    user = get_authenticated_user(
        authorization
    )

    if user["admin"] == True:
        db.update_entry("users", "id", user_id, {"validated" : True})