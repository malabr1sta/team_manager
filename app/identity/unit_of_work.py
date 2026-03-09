from typing import TYPE_CHECKING

from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,
)
from app.core.repositories.descriptor import LazyRepo
from app.core.repositories.identity import IdentityUserProtocol
from app.identity import repository as repo


class IdentityRepositoryProvider(AbstractSqlRepositoryProvider):
    """Identity context repository provider."""
    if TYPE_CHECKING:
        user: IdentityUserProtocol
    else:
        user = LazyRepo(repo.SQLAlchemyIdentityUserRepository)


class IdentitySQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[IdentityRepositoryProvider]
):
    ...
