from typing import TYPE_CHECKING

from app.core.repositories.descriptor import LazyRepo
from app.core.repositories.evaluations import (
    EvaluationUserProtocol,
    EvaluationTaskProtocol,
    EvaluationProtocol,
)
from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,
)
from app.evaluations import repository as repo


class EvaluationRepositoryProvider(AbstractSqlRepositoryProvider):
    if TYPE_CHECKING:
        user: EvaluationUserProtocol
        task: EvaluationTaskProtocol
        evaluation: EvaluationProtocol
    else:
        user = LazyRepo(repo.SQLAlchemyEvaluationUserRepository)
        task = LazyRepo(repo.SQLAlchemyEvaluationTaskRepository)
        evaluation = LazyRepo(repo.SQLAlchemyEvaluationRepository)


class EvaluationSQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[EvaluationRepositoryProvider]
):
    ...
