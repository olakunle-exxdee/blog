"""Posts router."""

from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, status, Path, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.schemas import PostCreate, CommentCreate
from app.database import get_db
from app.models import Post, Comment
from .auth import get_current_user


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


DbDependencies = Annotated[Session, Depends(get_db)]
UserDependencies = Annotated[Session, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_posts(user: UserDependencies, db: DbDependencies):
    """This function is used to read all the posts"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return db.query(Post).filter(Post.author_id == user.get("id")).all()


@router.post("/{post_id}/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(
    user: UserDependencies,
    db: DbDependencies,
    comment: CommentCreate,
    post_id: int = Path(gt=0),
):
    """This function is used to create a comment"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    new_post = db.query(Post).filter(Post.id == post_id).first()
    if new_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    db_comment = Comment(
        **comment.dict(),
        author_id=user.get("id"),
        post_id=post_id,
        created_at=datetime.now()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/{post_id}/comments", status_code=status.HTTP_200_OK)
async def read_comments(
    user: UserDependencies,
    db: DbDependencies,
    post_id: int = Path(gt=0),
    skip: int = 0,
    limit: int = 10,
):
    """This function is used to read all the comments in a post"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    comments = (
        db.query(Comment)
        .filter(Comment.author_id == user.get("id"))
        .filter(Comment.id == post_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments


@router.get("/{post_id}/with-comments", status_code=status.HTTP_200_OK)
def read_post_with_comments(
    user: UserDependencies, post_id: int, db: Session = Depends(get_db)
):
    """Query the post and eagerly load the related comments"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    post = (
        db.query(Post)
        .options(joinedload(Post.comments).joinedload(Comment.author))
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


@router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def read_single_post(
    user: UserDependencies, db: DbDependencies, post_id: int = Path(gt=0)
):
    """This function is used to read a single post"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    single_post = (
        db.query(Post)
        .filter(Post.author_id == user.get("id"))
        .filter(Post.id == post_id)
        .first()
    )
    if single_post is not None:
        return single_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(user: UserDependencies, db: DbDependencies, post: PostCreate):
    """This function is used to create a post"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=user.get("id"),
        created_at=datetime.now(),
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put("/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(
    user: UserDependencies,
    db: DbDependencies,
    post: PostCreate,
    post_id: int = Path(gt=0),
):
    """This function is used to update a post"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    db_post = (
        db.query(Post)
        .filter(Post.author_id == user.get("id"))
        .filter(Post.id == post_id)
        .first()
    )
    if db_post is not None:
        db_post.title = post.title
        db_post.content = post.content
        db.commit()
        db.refresh(db_post)
        return db_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    user: UserDependencies, db: DbDependencies, post_id: int = Path(gt=0)
):
    """This function is used to delete a post"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    post = (
        db.query(Post)
        .filter(Post.author_id == user.get("id"))
        .filter(Post.id == post_id)
        .first()
    )
    if post is not None:
        db.delete(post)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
