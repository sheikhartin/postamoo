import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from postamoo.routers import user_management, posts
from postamoo.database import Base, engine
from postamoo.config import MEDIA_UPLOAD_FOLDER, MEDIA_STORAGE_PATH


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    os.makedirs(MEDIA_STORAGE_PATH, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    # Yield to allow the application to start handling requests.
    yield


app = FastAPI(
    title='Postamoo',
    summary='Users can post multimedia content and interact with others.',
    version='v1',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

media_files_path = f'/{MEDIA_UPLOAD_FOLDER}'
media_files_directory = os.path.dirname(MEDIA_UPLOAD_FOLDER)
app.mount(
    media_files_path,
    StaticFiles(directory=MEDIA_STORAGE_PATH),
    name=media_files_directory,
)

app.include_router(user_management.router, tags=['User Management'])
app.include_router(posts.router, tags=['Posts'])
