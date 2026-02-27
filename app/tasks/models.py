from typing import Unpack
from datetime import datetime, timezone
from app.core.custom_types import ids, role, task_status, task_patch
from app.core.aggregate import AggregateRoot
from app.core.entity import Entity
from app.core.shared.models.users import BaseUser
from app.core.shared.events import tasks as task_event
from app.tasks import custom_exception

from dataclasses import dataclass


class TaskUser(BaseUser):
    ...


@dataclass(frozen=True)
class MemberTask:
    """Represents a task member with an assigned role."""
    user_id: ids.UserId
    team_id: ids.TeamId
    role: role.UserTaskRole


class Team(Entity):
    """Team for task's context."""

    def __init__(
            self, id: ids.TeamId,
            members: list[MemberTask]
    ):
        """Create a team with a unique identifier."""
        self._id = id
        self._members = members

    @property
    def id(self) -> ids.TeamId:
        """Return team identifier."""
        return self._id

    def get_member(
            self, user_id: ids.UserId, role: role.UserTaskRole
    ) -> MemberTask:
        """Return team member by user id or raise an error if not found."""
        for member in self.members:
            if member.user_id == user_id and member.role == role:
                return member
        raise custom_exception.TaskMemberNotFoundException(
            "User is not a team member")

    def add_member(
            self, user_id: ids.UserId, role: role.UserTaskRole
    ) -> MemberTask | None:
        """Add member in team"""
        if self.id is None:
            raise custom_exception.TaskTeamIdMissingException(
                "Cannot add member to a team without id")
        new_member = MemberTask(user_id, self._id, role)
        if new_member not in self._members:
            self._members.append(new_member)
            return new_member

    def remove_member(
            self, user_id: ids.UserId, role: role.UserTaskRole
    ) -> MemberTask:
        """Remove member in team"""
        member = self.get_member(user_id, role)
        self._members.remove(member)
        return member

    @property
    def members(self) -> tuple[MemberTask, ...]:
        """Return team members as an immutable collection."""
        return tuple(self._members)

    def is_member(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team member."""
        return any(
            member.user_id == user_id
            for member in self._members
        )

    def has_member(self, user_id: ids.UserId, role: role.UserTaskRole) -> bool:
            """Check whether the user is already a team member."""
            return MemberTask(user_id, self.id, role) in self.members

    def change_role(
        self,
        user_id: ids.UserId,
        old_role: role.UserTaskRole,
        new_role: role.UserTaskRole,
    ):
        "Change roles in team"

        old_member = MemberTask(user_id, self.id, old_role)
        new_member = MemberTask(user_id, self.id, new_role)

        if old_member not in self._members:
            raise custom_exception.TaskMemberNotFoundException(
                "User with this role not found"
            )

        if new_member in self._members:
            self._members.remove(old_member)
            return

        index = self._members.index(old_member)
        self._members[index] = new_member


class Comment(Entity):
    """A comment on a task with author and creation time."""

    def __init__(
            self, author_id: ids.UserId,
            task_id: ids.TaskId,
            text: str,
            team_id: ids.TeamId | None = None,
            id: ids.CommentId | None = None,
            created_at: datetime | None = None

    ):
        self._id = id
        self._team_id = team_id
        self._task_id = task_id
        self._author_id = author_id
        self._text = text
        self._created_at = created_at

    @property
    def id(self) -> ids.CommentId | None:
        return self._id

    @property
    def team_id(self) -> ids.TeamId | None:
        return self._team_id

    @property
    def task_id(self) -> ids.TaskId:
        return self._task_id

    @property
    def author_id(self) -> ids.UserId:
        return self._author_id

    @property
    def text(self) -> str:
        return self._text

    @property
    def created_at(self) -> datetime | None:
        return self._created_at


class Task(Entity, AggregateRoot):
    """
    Represents a task in a team.

    Attributes:
        supervisor: The team member who supervises the task.
        deadline: The task's due date and time.
        title: The task title.
        description: The task description.
        id: Optional unique identifier of the task.
        executor: Optional team member assigned to execute the task.
        created_at: Optional task creation timestamp.
        updated_at: Optional task update timestamp.
        _status: Current status of the task (default: OPEN).
        _comments: List of comments attached to the task.
    """

    def __init__(self,
                 supervisor_id: ids.UserId,
                 deadline: datetime,
                 title: str,
                 description: str,
                 id: ids.TaskId | None = None,
                 team_id: ids.TeamId | None = None,
                 status: task_status.TaskStatus = task_status.TaskStatus.OPEN,
                 executor_id: ids.UserId | None = None,
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None

    ):
        AggregateRoot.__init__(self)
        self._id = id
        self._supervisor_id = supervisor_id
        self._team_id = team_id
        self._title = title
        self._description = description
        self._status = status
        self._deadline = deadline
        self._created_at = created_at
        self._updated_at = updated_at
        self._executor_id = executor_id
        self._deleted = False

    @property
    def id(self) -> ids.TaskId | None:
        """Return task identifier."""
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def supervisor_id(self) -> ids.UserId:
        return self._supervisor_id

    @property
    def executor_id(self) -> ids.UserId | None:
        return self._executor_id

    @property
    def status(self) -> task_status.TaskStatus:
        return self._status

    @property
    def team_id(self) -> ids.TeamId | None:
        """Return task identifier."""
        return self._team_id

    @property
    def deadline(self) -> datetime | None:
        return self._deadline

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    @property
    def deleted(self) -> bool:
        return self._deleted

    def check_member(
            self, user_id: ids.UserId, role: role.UserTaskRole,
            team: Team
    ):
        """Check that the member belongs to the team or has ANY role."""
        if not team.has_member(user_id, role):
            raise custom_exception.TaskMemberException(
                f"Member {user_id} is not part of this team"
                f"or has invalid role."
            )

    def set_executor(
            self, user_id: ids.UserId,
            team: Team
    ):
        self.check_member(user_id, role.UserTaskRole.MEMBER, team)
        self._executor_id = user_id
        self.record_event(
            task_event.TaskUpdated(
                task_id=int(self._id or 0),
                team_id=int(self._team_id or 0),
                supervisor_id=int(self._supervisor_id),
                executor_id=int(self._executor_id),
                status=self._status.value,
            )
        )

    def update_task(
        self, **args: Unpack[task_patch.TaskUpdateArgs]
    ):
        allowed_fields = {
            "title": "_title",
            "description": "_description",
            "status": "_status",
            "deleted": "_deleted",
        }

        for arg_name, attr_name in allowed_fields.items():
            if arg_name in args:
                setattr(self, attr_name, args[arg_name])

        self._updated_at = datetime.now(timezone.utc)
        self.record_event(
            task_event.TaskUpdated(
                task_id=int(self._id or 0),
                team_id=int(self._team_id or 0),
                supervisor_id=int(self._supervisor_id),
                executor_id=int(self._executor_id) if self._executor_id else None,
                status=self._status.value,
            )
        )

    def mark_created_event(self) -> None:
        if self._id is None or self._team_id is None:
            return
        self.record_event(
            task_event.TaskCreated(
                task_id=int(self._id),
                team_id=int(self._team_id),
                supervisor_id=int(self._supervisor_id),
                executor_id=int(self._executor_id) if self._executor_id else None,
                status=self._status.value,
            )
        )
