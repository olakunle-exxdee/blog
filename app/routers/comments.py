""" This module contains the routers for the comments. """

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session
from app.schemas import CommentBase
from app.database import get_db
from app.models import Comment
from .auth import get_current_user


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


DbDependencies = Annotated[Session, Depends(get_db)]
UserDependencies = Annotated[Session, Depends(get_current_user)]


@router.get("/{comment_id}", status_code=status.HTTP_200_OK)
async def read_single_comment(
    user: UserDependencies, db: DbDependencies, comment_id: int = Path(gt=0)
):
    """This function is used to read a single comment"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    single_comment = (
        db.query(Comment)
        .filter(Comment.author_id == user.get("id"))
        .filter(Comment.id == comment_id)
        .first()
    )
    if single_comment is not None:
        return single_comment
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )


@router.put("/{comment_id}", status_code=status.HTTP_200_OK)
async def update_comment(
    user: UserDependencies,
    db: DbDependencies,
    comment: CommentBase,
    comment_id: int = Path(gt=0),
):
    """This function is used to update a comment"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    db_comment = (
        db.query(Comment)
        .filter(Comment.author_id == user.get("id"))
        .filter(Comment.id == comment_id)
        .first()
    )
    if db_comment is not None:
        db_comment.content = comment.content
        db.commit()
        db.refresh(db_comment)
        return db_comment
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    user: UserDependencies, db: DbDependencies, comment_id: int = Path(gt=0)
):
    """This function is used to delete a comment"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    db_comment = (
        db.query(Comment)
        .filter(Comment.author_id == user.get("id"))
        .filter(Comment.id == comment_id)
        .first()
    )
    if db_comment is not None:
        db.delete(db_comment)
        db.commit()
        return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )
