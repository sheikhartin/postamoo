from sqlalchemy.orm import Session

from postamoo import models, schemas, crud


def test_create_user_profile(test_db_session: Session) -> None:
    user_profile_data = schemas.UserProfileCreate(
        username='michaelbrown',
        display_name='Michael Brown',
        bio='Writer and journalist. Interests include history, politics, and sports.',
        location='Boston, MA',
    )
    created_user_profile = crud.create_user_profile(
        db=test_db_session,
        user_profile=user_profile_data,
    )
    assert created_user_profile.username == 'michaelbrown'
    assert created_user_profile.display_name == 'Michael Brown'
    assert created_user_profile.bio == (
        'Writer and journalist. Interests include '
        'history, politics, and sports.'
    )
    assert created_user_profile.location == 'Boston, MA'


def test_get_user_profile_by_id(
    test_db_session: Session,
    create_test_user: models.UserProfile,
) -> None:
    retrieved_user_profile = crud.get_user_profile_by_id(
        db=test_db_session, user_id=create_test_user.id
    )
    assert retrieved_user_profile.id == create_test_user.id
    assert retrieved_user_profile.username == create_test_user.username
    assert retrieved_user_profile.display_name == create_test_user.display_name
    assert retrieved_user_profile.bio == create_test_user.bio
    assert retrieved_user_profile.location == create_test_user.location


def test_create_post(
    test_db_session: Session,
    create_test_user: models.UserProfile,
) -> None:
    post_data = schemas.PostCreate(
        title='Test Post',
        text_content='This is a test post.',
    )
    created_post = crud.create_post(
        db=test_db_session, post=post_data, author_id=create_test_user.id
    )
    assert created_post.title == 'Test Post'
    assert created_post.text_content == 'This is a test post.'
    assert created_post.author_id == create_test_user.id


def test_get_posts(
    test_db_session: Session,
    create_test_post: models.Post,
) -> None:
    posts = crud.get_posts(db=test_db_session)
    assert len(posts) >= 1
    found_post = next(
        (post for post in posts if post.id == create_test_post.id), None
    )
    assert found_post is not None
    assert found_post.title == create_test_post.title
    assert found_post.text_content == create_test_post.text_content
    assert found_post.author_id == create_test_post.author_id


def test_get_post_by_id(
    test_db_session: Session,
    create_test_post: models.Post,
) -> None:
    retrieved_post = crud.get_post_by_id(
        db=test_db_session, post_id=create_test_post.id
    )
    assert retrieved_post.id == create_test_post.id
    assert retrieved_post.title == create_test_post.title
    assert retrieved_post.text_content == create_test_post.text_content
    assert retrieved_post.author_id == create_test_post.author_id


def test_delete_post_by_id(
    test_db_session: Session,
    create_test_user: models.UserProfile,
    create_test_post: models.Post,
) -> None:
    crud.delete_post_by_id(
        db=test_db_session,
        post_id=create_test_post.id,
        current_user_id=create_test_user.id,
    )
    deleted_post = crud.get_post_by_id(
        db=test_db_session, post_id=create_test_post.id
    )
    assert deleted_post is None


def test_create_comment(
    test_db_session: Session,
    create_test_user: models.UserProfile,
    create_test_post: models.Post,
) -> None:
    comment_data = schemas.CommentCreate(
        content='This is a test comment.',
    )
    created_comment = crud.create_comment(
        db=test_db_session,
        comment=comment_data,
        post_id=create_test_post.id,
        author_id=create_test_user.id,
    )
    assert created_comment.content == 'This is a test comment.'
    assert created_comment.post_id == create_test_post.id
    assert created_comment.author_id == create_test_user.id


def test_get_post_comments(
    test_db_session: Session,
    create_test_post: models.Post,
    create_test_comment: models.Comment,
) -> None:
    comments = crud.get_post_comments(
        db=test_db_session, post_id=create_test_post.id
    )
    assert len(comments) >= 1
    found_comment = next(
        (
            comment
            for comment in comments
            if comment.id == create_test_comment.id
        ),
        None,
    )
    assert found_comment is not None
    assert found_comment.content == create_test_comment.content
    assert found_comment.post_id == create_test_comment.post_id
    assert found_comment.author_id == create_test_comment.author_id


def test_get_comment_by_id(
    test_db_session: Session,
    create_test_comment: models.Comment,
) -> None:
    retrieved_comment = crud.get_comment_by_id(
        db=test_db_session, comment_id=create_test_comment.id
    )
    assert retrieved_comment.id == create_test_comment.id
    assert retrieved_comment.content == create_test_comment.content
    assert retrieved_comment.post_id == create_test_comment.post_id
    assert retrieved_comment.author_id == create_test_comment.author_id


def test_delete_comment_by_id(
    test_db_session: Session,
    create_test_user: models.UserProfile,
    create_test_comment: models.Comment,
) -> None:
    crud.delete_comment_by_id(
        db=test_db_session,
        comment_id=create_test_comment.id,
        current_user_id=create_test_user.id,
    )
    deleted_comment = crud.get_comment_by_id(
        db=test_db_session, comment_id=create_test_comment.id
    )
    assert deleted_comment is None
