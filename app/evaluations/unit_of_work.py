from app.core.repositories.descriptor import LazyRepo
from app.core.unit_of_work import AbstractSqlRepositoryProvider, SQLAlchemyUnitOfWork
from app.evaluations import repository as repo


class EvaluationRepositoryProvider(AbstractSqlRepositoryProvider):
    user = LazyRepo(repo.SQLAlchemyEvaluationUserRepository)
    task = LazyRepo(repo.SQLAlchemyEvaluationTaskRepository)
    evaluation = LazyRepo(repo.SQLAlchemyEvaluationRepository)


class EvaluationSQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[EvaluationRepositoryProvider]
):
    ...
