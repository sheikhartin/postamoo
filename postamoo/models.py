from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    ARRAY,
)
from sqlalchemy.orm import relationship

from postamoo.database import Base


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(35), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    avatar = Column(String(35))
    bio = Column(String(300))
    location = Column(String(200))

    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='author')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    text_content = Column(Text)
    media_files = Column(ARRAY(String(40)))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    author_id = Column(
        Integer,
        ForeignKey('user_profiles.id'),
        nullable=False,
    )

    author = relationship('UserProfile', back_populates='posts')
    comments = relationship('Comment', back_populates='post')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    author_id = Column(
        Integer,
        ForeignKey('user_profiles.id'),
        nullable=False,
    )

    author = relationship('UserProfile', back_populates='comments')
    post = relationship('Post', back_populates='comments')
