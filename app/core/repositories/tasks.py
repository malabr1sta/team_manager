from typing import Protocol, runtime_checkable

from app.tasks.models import (
    MemberTask,
    TaskUser,
    Task,
    Team,
    Comment
)


@runtime_checkable
class TaskUserProtocol(Protocol):
    """Protocol user's repository"""

    async def save(self, user: TaskUser) -> None:
        ...

    async def get_by_id(self, id: int) -> TaskUser | None:
        ...


@runtime_checkable
class TaskMemberProtocol(Protocol):

    async def get_by_user(
        self, user_id: int
    ) -> list[MemberTask]:
        ...

    async def get_by_user_and_team(
        self,
        user_id: int,
        team_id: int,
    ) -> list[MemberTask]:
        ...

    async def save(self, member: MemberTask) -> None:
        ...


@runtime_checkable
class TaskTeamProtocol(Protocol):

    async def get_by_id(self, id: int) -> Team | None:
        ...

    async def save(self, team: Team) -> None:
        ...


@runtime_checkable
class TaskCommentProtocol(Protocol):

    async def get_by_task_id(self, task_id: int) ->  list[Comment]:
        ...

    async def save(self, comment: Comment) -> Comment:
        ...


@runtime_checkable
class TaskProtocol(Protocol):

    async def get_by_id(self, id: int) -> Task | None:
        ...

    async def get_by_supervisor(self, id: int) -> list[Task]:
        ...

    async def get_by_team(self, id: int) -> list[Task]:
        ...

    async def get_by_executor(self, id: int) -> list[Task]:
        ...

    async def save(self, task: Task) -> None:
        ...
