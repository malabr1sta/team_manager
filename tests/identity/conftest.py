import pytest
from app.identity.models import User
from app.core.custom_types import ids


@pytest.fixture
def user_factory():
    """
    Class-level fixture returning a factory function to create Users
    with custom email and optional username.
    """
    def _create(id: int, email: str, username: str | None = None) -> User:
        return User(id=ids.UserId(id), email=email, username=username)
    return _create

# @pytest.fixture
# def team_fixture(user_factory):
#     """
#     Fixture return UserId for admin team
#     """
#     user = user_factory(email="ad@in.com", username="admin")
#     team = domain.Team(user.id, "test_team")
#     return (user.id, team)
