""" This module contains the schemas for the application """

from typing import List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class EnumRole(str, Enum):
    """Enum class for role"""

    ADMIN = "admin"
    USER = "user"


class CreatUserRequest(BaseModel):
    """create user request"""

    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    role: EnumRole


class TokenRequest(BaseModel):
    """Token model"""

    access_token: str
    token_type: str


class PostCreate(BaseModel):
    """Pydantic model for creating a post"""

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=1000)


class PostBase(BaseModel):
    """Base schema for Post"""

    title: str
    content: str
    author_id: int
    created_at: datetime


class CommentCreate(BaseModel):
    """Pydantic model for creating a post"""

    content: str = Field(min_length=3, max_length=1000)


class CommentBase(BaseModel):
    """This is the Comment schema for the application"""

    id: int
    content: str
    author_id: int
    post_id: int
    created_at: datetime


class PostWithComments(PostBase):
    """This is the Post schema for the application"""

    comments: List[CommentBase]


class UserVerification(BaseModel):
    """This class is used to validate the request body for the user verification."""

    password: str
    new_password: str = Field(min_length=6)
