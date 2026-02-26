from app.identity.orm_models import UserORM
from app.identity import models
from app.core.custom_types import ids


class UserMapper:
    @staticmethod
    def to_domain(orm: UserORM) -> models.User:
        user = models.User(
            id=ids.UserId(orm.id),
            email=orm.email,
            username=orm.username,
            deleted=orm.deleted,
        )
        user.deleted = orm.deleted
        return user

    # @staticmethod
    # def to_orm(domain: models.User) -> UserORM:
    #     pass

    @staticmethod
    def update_orm(orm: UserORM, domain: models.User) -> None:
        orm.email = domain.email
        orm.username = domain.username
        orm.deleted = domain.deleted
        orm.is_active = not domain.deleted
