"""This module contains the routes for the authentication of the user."""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import CreatUserRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


DbDependencies = Annotated[Session, Depends(get_db)]


def authenticate_user(db: Session, username: str, password: str):
    """This function is used to authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expire_delta: timedelta
):
    """This function is used to create the access token."""
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expire_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
):
    """This function is used to get the current user."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not validate user",
            )

        return {"username": username, "id": user_id, "role": user_role}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user"
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: DbDependencies, create_user_request: CreatUserRequest):
    """This function is used to create a user"""
    db_user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt.hash(create_user_request.password),
    )
    if (
        db.query(User)
        .filter(or_(User.username == db_user.username, User.email == db_user.email))
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    db: DbDependencies, form_data: OAuth2PasswordRequestForm = Depends()
):
    """This function is used to login for an access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expire_delta=timedelta(minutes=15),
    )
    return {"access_token": token, "token_type": "bearer"}
