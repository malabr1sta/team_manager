import pytest
from contextlib import nullcontext
from app.identity.custom_exception import UserDeleteException


class TestUser:

    def test_user_entity_eq(self, user_factory):
        user1 = user_factory(id=1, email="test@mail.com", username="usernmae")
        user2 = user_factory(id=1, email="test1@mail.com", username="user")
        assert user1 == user2

    def test_delete_user(self, user_factory):
        """Test User delete with valid"""
        user = user_factory(id=1, email="test@email")
        user.delete()
        assert user.deleted

    @pytest.mark.parametrize(
        "email,username,new_email,new_username,result",
        [
            (
                "test@ex.com", "bob", "email_invalid", "new_name",
                pytest.raises(ValueError)
            ),
            (
                "test@ex.com", "bob", "new@email", "new_name",
                nullcontext(0)
            ),


        ],
    )
    def test_update_user(
            self, email, username,
            new_email, new_username,
            result,
            user_factory
    ):
        """Test User update with valid
        and invalid email/username combinations."""
        with result as expected:
            user = user_factory(id=1, email=email, username=username)

            if expected is not None:
                user.update(email=new_email, username=new_username)
                assert user.email == new_email
                assert user.username == new_username

    def test_delete_and_update(self, user_factory):
        """Test User delete, then update"""
        user = user_factory(id=1, email="test@email")
        user.delete()
        with pytest.raises(UserDeleteException):
            user.update(username="new_name")
