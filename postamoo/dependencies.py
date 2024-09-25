from typing import Iterator, AsyncIterator

import httpx
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

from postamoo import models, crud
from postamoo.database import SessionLocal
from postamoo.config import AUTH_PROVIDER_URL


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


async def get_access_token(request: Request) -> str:
    access_token = request.cookies.get('access_token')
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated.',
        )
    return access_token


async def get_current_user(
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_httpx_client),
) -> models.UserProfile:
    try:
        response = await client.get(
            f'{AUTH_PROVIDER_URL}/users/me/',
            cookies={'access_token': access_token},
        )
        response.raise_for_status()
        response_content = response.json()
    except httpx.HTTPError as e:
        error_response = e.response.json()
        error_detail = error_response.get('detail', 'Unknown error!')
        raise HTTPException(
            status_code=e.response.status_code,
            detail=error_detail,
        )

    db_user_profile = crud.get_user_profile_by_username(
        db=db, username=response_content['username']
    )
    if db_user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found in the database.',
        )
    return db_user_profile
