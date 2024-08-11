"""User router."""

from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User
from app.database import get_db
from .auth import get_current_user
from app.schemas import UserVerification


router = APIRouter(
    prefix="/user",
    tags=["user"],
)
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

DbDependencies = Annotated[Session, Depends(get_db)]
UserDependencies = Annotated[Session, Depends(get_current_user)]


@router.get("/")
async def read_current_user(user: UserDependencies, db: DbDependencies):
    """This function is used to return the current user."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    current_user = db.query(User).filter(User.id == user.get("id")).first()
    return current_user


@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    user: UserDependencies, db: DbDependencies, user_verification: UserVerification
):
    """this function is used to update_password"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if not bcrypt.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    user_model.hashed_password = bcrypt.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {"message": "Password updated successfully"}
