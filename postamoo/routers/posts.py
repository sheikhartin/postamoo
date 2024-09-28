from typing import Optional

from fastapi import (
    APIRouter,
    Response,
    Depends,
    Body,
    UploadFile,
    File,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from postamoo import models, schemas, crud
from postamoo.dependencies import get_db, get_current_user

router = APIRouter()


@router.get('/posts/', response_model=list[schemas.Post])
async def read_posts(db: Session = Depends(get_db)):
    return crud.get_posts(db=db)


@router.get('/posts/{post_id}/', response_model=schemas.Post)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    db_post = crud.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found.',
        )
    return db_post


@router.post('/posts/', response_model=schemas.Post)
async def create_post(
    title: str = Body(...),
    text_content: Optional[str] = Body(None),
    media_files: list[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(get_current_user),
):
    try:
        new_post = schemas.PostCreate(
            title=title,
            text_content=text_content,
            media_files=media_files,
        )
        return crud.create_post(
            db=db, post=new_post, author_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Failed to create post: {str(e)}',
        )


@router.delete('/posts/{post_id}/')
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(get_current_user),
):
    crud.delete_post_by_id(
        db=db, post_id=post_id, current_user_id=current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.get('/posts/{post_id}/comments/', response_model=list[schemas.Comment])
async def read_post_comments(
    post_id: int,
    db: Session = Depends(get_db),
):
    db_post = crud.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Post not found.'
        )
    return crud.get_post_comments(db=db, post_id=post_id)


@router.post('/posts/{post_id}/comments/', response_model=schemas.Comment)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(get_current_user),
):
    return crud.create_comment(
        db=db, comment=comment, post_id=post_id, author_id=current_user.id
    )


@router.delete('/posts/{post_id}/comments/{comment_id}/')
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(get_current_user),
):
    crud.delete_comment_by_id(
        db=db, comment_id=comment_id, current_user_id=current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT, content=None)
