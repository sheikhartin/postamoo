from typing import Optional

import httpx
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
from postamoo.dependencies import get_db, get_httpx_client, get_current_user
from postamoo.config import AUTH_PROVIDER_URL

router = APIRouter()


@router.post('/login/')
async def login(
    response: Response,
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_httpx_client),
):
    try:
        login_response = await client.post(
            f'{AUTH_PROVIDER_URL}/login/',
            json={'username': username, 'password': password},
        )
        login_response.raise_for_status()
        login_response_content = login_response.json()
    except httpx.HTTPError as e:
        error_response = e.response.json()
        error_detail = error_response.get('detail', 'Unknown error!')
        raise HTTPException(
            status_code=e.response.status_code,
            detail=error_detail,
        )

    db_user_profile = crud.get_user_profile_by_username(
        db=db, username=login_response_content['username']
    )
    if db_user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found in the Postamoo database.',
        )

    return login_response_content


@router.post('/logout/')
async def logout(
    response: Response,
    client: httpx.AsyncClient = Depends(get_httpx_client),
):
    try:
        logout_response = await client.post(f'{AUTH_PROVIDER_URL}/logout/')
        logout_response.raise_for_status()
    except httpx.HTTPError as e:
        error_response = e.response.json()
        error_detail = error_response.get('detail', 'Unknown error!')
        raise HTTPException(
            status_code=e.response.status_code,
            detail=error_detail,
        )
    return {'message': 'Logout successful.'}


@router.post('/users/', response_model=schemas.UserProfileBase)
async def create_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    display_name: str = Body(...),
    bio: Optional[str] = Body(None),
    location: Optional[str] = Body(None),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_httpx_client),
):
    files = {}
    if avatar is not None:
        await avatar.seek(0)
        file_content = await avatar.read()
        files['avatar'] = (avatar.filename, file_content, avatar.content_type)

    try:
        create_response = await client.post(
            f'{AUTH_PROVIDER_URL}/users/',
            data={
                'username': username,
                'email': email,
                'password': password,
                'display_name': display_name,
                'bio': bio,
                'location': location,
            },
            files=files,
        )
        create_response.raise_for_status()
        create_response_content = create_response.json()
    except httpx.HTTPError as e:
        error_response = e.response.json()
        error_detail = error_response.get('detail', 'Unknown error!')
        raise HTTPException(
            status_code=e.response.status_code,
            detail=error_detail,
        )

    try:
        new_user_profile = schemas.UserProfileCreate(
            username=create_response_content['username'],
            display_name=create_response_content['profile']['display_name'],
            avatar=create_response_content['profile']['avatar'],
            bio=create_response_content['profile']['bio'],
            location=create_response_content['profile']['location'],
        )
        return crud.create_user_profile(db=db, user_profile=new_user_profile)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to parse user profile: {str(e)}',
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Failed to create user: {str(e)}',
        )


@router.get('/users/me/')
async def read_users_me(
    current_user: models.UserProfile = Depends(get_current_user),
):
    return current_user
