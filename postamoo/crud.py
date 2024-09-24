from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from postamoo import models, schemas


def get_user_profile_by_id(
    db: Session,
    user_id: int,
) -> Optional[models.UserProfile]:
    return (
        db.query(models.UserProfile)
        .filter(models.UserProfile.id == user_id)
        .first()
    )


def get_user_profile_by_username(
    db: Session,
    username: str,
) -> Optional[models.UserProfile]:
    return (
        db.query(models.UserProfile)
        .filter(models.UserProfile.username == username)
        .first()
    )


def create_user_profile(
    db: Session,
    user_profile: schemas.UserProfileCreate,
) -> models.UserProfile:
    db_user_profile = models.UserProfile(**user_profile.dict())
    db.add(db_user_profile)
    db.commit()
    db.refresh(db_user_profile)
    return db_user_profile


def get_posts(db: Session) -> Optional[list[models.Post]]:
    return db.query(models.Post).all()


def get_post_by_id(db: Session, post_id: int) -> Optional[models.Post]:
    return (
        db.query(models.Post)
        .options(selectinload(models.Post.comments))
        .filter(models.Post.id == post_id)
        .first()
    )


def create_post(
    db: Session,
    post: schemas.PostCreate,
    author_id: int,
) -> models.Post:
    db_post = models.Post(**post.dict(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post_by_id(
    db: Session,
    post_id: int,
    current_user_id: int,
) -> None:
    db_post = get_post_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found.',
        )
    elif db_post.author_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this post.',
        )
    db.delete(db_post)
    db.commit()


def get_post_comments(
    db: Session,
    post_id: int,
) -> Optional[list[models.Comment]]:
    return (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id)
        .all()
    )


def get_comment_by_id(db: Session, comment_id: int) -> Optional[models.Post]:
    return (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id)
        .first()
    )


def create_comment(
    db: Session,
    comment: schemas.CommentCreate,
    post_id: int,
    author_id: int,
) -> models.Comment:
    db_post = get_post_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found.',
        )

    db_comment = models.Comment(
        **comment.dict(),
        post_id=post_id,
        author_id=author_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment_by_id(
    db: Session,
    comment_id: int,
    current_user_id: int,
) -> None:
    db_comment = get_comment_by_id(db, comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found.',
        )
    elif db_comment.author_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this comment.',
        )
    db.delete(db_comment)
    db.commit()
