import os
from urllib.parse import urlparse
from typing import Optional, Any, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from postamoo import models, schemas, crud
from postamoo.main import app
from postamoo.database import Base
from postamoo.dependencies import get_db
from postamoo.config import TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope='function')
def test_db_session() -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, 'after_transaction_end')
    def reset_transaction(
        session: Session,
        transaction: Optional[Any],
    ) -> None:
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def test_client(test_db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        try:
            yield test_db_session
        finally:
            test_db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope='function')
def create_test_user(test_db_session: Session) -> models.UserProfile:
    user_profile_data = schemas.UserProfileCreate(
        username='johndoe',
        display_name='John Doe',
    )
    return crud.create_user_profile(
        db=test_db_session, user_profile=user_profile_data
    )


@pytest.fixture(scope='function')
def create_test_post(
    test_db_session: Session,
    create_test_user: models.UserProfile,
) -> models.Post:
    post_data = schemas.PostCreate(
        title='Test Post',
        text_content='This is a test post.',
    )
    return crud.create_post(
        db=test_db_session, post=post_data, author_id=create_test_user.id
    )


@pytest.fixture(scope='function')
def create_test_comment(
    test_db_session: Session,
    create_test_user: models.UserProfile,
    create_test_post: models.Post,
) -> models.Comment:
    comment_data = schemas.CommentCreate(
        content='This is a test comment.',
    )
    return crud.create_comment(
        db=test_db_session,
        comment=comment_data,
        post_id=create_test_post.id,
        author_id=create_test_user.id,
    )


@pytest.fixture(scope='session', autouse=True)
def teardown_test_database() -> Iterator[None]:
    yield

    Base.metadata.drop_all(bind=engine)

    parsed_url = urlparse(TEST_DATABASE_URL)
    if parsed_url.scheme in ('sqlite',):
        db_file_path = parsed_url.path.strip('/')
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
            print(f'Removed test database file: {db_file_path}')
        else:
            print(f'Test database file does not exist: {db_file_path}')
