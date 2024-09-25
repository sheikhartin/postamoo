from datetime import datetime
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=35)
    display_name: str = Field(..., min_length=3, max_length=50)
    avatar: Optional[str] = Field(None, max_length=35)
    bio: Optional[str] = Field(None, max_length=300)
    location: Optional[str] = Field(None, max_length=200)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)


class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    text_content: Optional[str] = None
    media_files: Optional[list[str]] = None


class PostCreate(PostBase):
    media_files: Optional[list[UploadFile]] = None


class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    created_at: datetime
    author_id: int = Field(..., ge=1)
    comments: Optional[list['Comment']] = None


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    created_at: datetime
    post_id: int = Field(..., ge=1)
    author_id: int = Field(..., ge=1)
