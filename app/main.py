""" This is the main file for the FastAPI application """

from fastapi import FastAPI
from app.routers import posts, auth, user, comments
from app import models
from app.database import engine


app = FastAPI()


@app.get("/")
async def root():
    """This is the root path for the FastAPI application"""
    return {"message": "Welcome to the Personal Blog API"}


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(posts.router)
app.include_router(comments.router)


models.Base.metadata.create_all(bind=engine)  # Create the database schema
