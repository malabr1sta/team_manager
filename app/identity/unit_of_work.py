from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,
)
from app.core.repositories.descriptor import LazyRepo
from app.identity import repository as repo


class IdentityRepositoryProvider(AbstractSqlRepositoryProvider):
    """Identity context repository provider."""
    user = LazyRepo(repo.SQLAlchemyIdentityUserRepository)


class IdentitySQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[IdentityRepositoryProvider]
):
    ...
