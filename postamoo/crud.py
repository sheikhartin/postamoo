import os
import shutil
import mimetypes
import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from postamoo import models, schemas
from postamoo.config import MEDIA_STORAGE_PATH, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE


def _create_unique_filename(filename: str) -> str:
    unique_id = uuid.uuid4().hex[:15]
    _, file_extension = os.path.splitext(filename)
    return f'{unique_id}{file_extension}'


def _save_media_file(file: UploadFile) -> str:
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type in [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
    ]:
        if file.size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    'Image file size exceeds the limit of '
                    f'{MAX_IMAGE_SIZE / (1024 * 1024)} MB.'
                ),
            )
    elif mime_type in [
        'video/mp4',
        'video/mpeg',
        'video/quicktime',
        'video/x-msvideo',
    ]:
        if file.size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    'Video file size exceeds the limit of '
                    f'{MAX_VIDEO_SIZE / (1024 * 1024)} MB.'
                ),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unsupported media type.',
        )

    filename = _create_unique_filename(file.filename)
    file_path = os.path.join(MEDIA_STORAGE_PATH, filename)
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    return filename


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
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def create_post(
    db: Session,
    post: schemas.PostCreate,
    author_id: int,
) -> models.Post:
    media_files = []
    if post.media_files is not None:
        for file in post.media_files:
            saved_file_name = _save_media_file(file)
            media_files.append(saved_file_name)

    db_post = models.Post(
        **post.dict(exclude={'media_files'}),
        media_files=media_files,
        author_id=author_id,
    )
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
