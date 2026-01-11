from datetime import datetime, timezone
from dataclasses import dataclass
from app.core.custom_types import ids, role, task_status
from app.core.entity import Entity
from app.teams import custom_exception

from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Member:
    """Represents a team member with an assigned role."""
    user_id: ids.UserId
    team_id: ids.TeamId | None
    role: role.UserRole


class Team(Entity):
    """Team aggregate root."""

    def __init__(
            self, id: ids.TeamId | None = None,
            members: list[Member] | None = None
    ):
        """Create a team with a unique identifier."""
        self._id = id
        self._members = members if members is not None else []

    @property
    def id(self) -> ids.TeamId | None:
        """Return team identifier."""
        return self._id

    @property
    def members(self) -> tuple[Member, ...]:
        """Return team members as an immutable collection."""
        return tuple(self._members)

    def get_member(self, user_id: ids.UserId, role: role.UserRole) -> Member:
        """Return team member by user id or raise an error if not found."""
        for member in self._members:
            if member.user_id == user_id and member.role == role:
                return member
        raise custom_exception.MemberNotFoundException(
            "User is not a team member")

    def is_admin(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team admin."""
        return any(
            member.user_id == user_id and member.role == role.UserRole.ADMIN
            for member in self._members
        )

    def is_member(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team admin."""
        return any(
            member.user_id == user_id
            for member in self._members
        )

    def has_member(self, member: Member) -> bool:
        """Check whether the user is already a team member."""
        return member in self.members


def create_team(user_id: ids.UserId, team_id: ids.TeamId ) -> Team:
    """Funtions for create team"""
    admin = Member(user_id, team_id, role.UserRole.ADMIN)
    return Team(team_id, [admin])


class TeamManagement(ABC):
    """Base class for team management actions requiring admin access."""

    def __init__(self, team: Team, admin_id: ids.UserId):
        """Initialize management context and validate admin permissions."""
        if not team.is_admin(admin_id):
            raise custom_exception.MemberNotAdminException(
                "Member is not at team admin"
            )
        self._team = team
        self._admin_id = admin_id

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionAddMemberTeam(TeamManagement):
    """Add a new member to the team."""

    def execute(self, user_id: ids.UserId, role: role.UserRole):
        if self._team.id is None:
            raise custom_exception.TeamIdMissingException(
                "Cannot add member to a team without id")
        new_member = Member(user_id, self._team.id, role)
        if not self._team.has_member(new_member):
            self._team._members.append(new_member)


class ActionRemoveMemberTeam(TeamManagement):
    """Remove an existing member from the team."""

    def execute(self, member: Member):
        if self._team.has_member(member):
            self._team._members.remove(member)



class ActionAssigningRolesTeam(TeamManagement):
    "Assigning roles in team"

    def execute(self, old_member: Member, new_role: role.UserRole):
        if self._team.has_member(old_member):
            new_member = Member(
                user_id=old_member.user_id,
                team_id=old_member.team_id,
                role=new_role
            )
            if not self._team.has_member(new_member):
                self._team._members = [
                    new_member if member == old_member else member
                    for member in self._team._members
                ]
            else:
                self._team._members.remove(old_member)


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
    def team_id(self) -> ids.TeamId:
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


class Task(Entity):
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
        self._id = id
        self._supervisor_id = supervisor_id
        self._team_id = team_id
        self._title = title
        self._description = description
        self._status = status
        self._deadline = deadline
        self._comments: list[Comment] = []
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

    @property
    def comments(self) -> tuple[Comment, ...]:
        """Return task comments as an immutable collection."""
        return tuple(self._comments)

    def check_member(self, member: Member, team: Team):
        """Check that the member belongs to the team or has ANY role."""
        if not team.has_member(member):
            raise custom_exception.TaskMemberException(
                f"Member {member.user_id} is not part of this team"
                f"or has invalid role."
            )


# datetime.now(timezone.utc)


def create_task(
        user_id: ids.UserId,
        team: Team,
        deadline: datetime,
        title: str,
        description: str,
) -> Task:
    """Create a new task supervised by a manager;
    deadline must be in the future."""

    manager = team.get_member(user_id, role.UserRole.MANAGER)
    now_time = datetime.now(timezone.utc)

    if deadline < now_time:
        raise custom_exception.TaskDeadlineException(
            "The deadline can't be in the past."
        )

    task = Task(
        supervisor_id=manager.user_id,
        team_id=team.id,
        title=title,
        description=description,
        deadline=deadline,
        created_at=now_time,
        updated_at=now_time
    )

    return task


class TaskManagement(ABC):
    """Base class for task management."""

    def __init__(self, task: Task, user_id: ids.UserId):
        """Initialize management context."""
        if task.supervisor_id != user_id:
            raise custom_exception.TaskSupervisorException(
                "Member is not at task supervisor"
            )
        self._task = task

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionAppointmentExecutorTask(TaskManagement):
    """Assigns an executor to the task."""

    def execute(self, user_id: ids.UserId, team: Team):
        """Validates the member and sets them as the task executor."""
        member = Member(
            user_id,
            self._task.team_id,
            role.UserRole.MEMBER
        )
        self._task.check_member(member, team)
        self._task._executor_id = user_id


class ActionUpdateTask(TaskManagement):
    """Update fields to the task"""

    def execute(self, **args):
        allowed_fields = {
            "title": "_title",
            "description": "_description",
            "status": "_status",
            "deleted": "_deleted",
        }

        for arg_name, attr_name in allowed_fields.items():
            if arg_name in args:
                setattr(self._task, attr_name, args[arg_name])

        self._task._updated_at = datetime.now(timezone.utc)


class CommentManagement(ABC):
    """Base class for comment management."""

    def __init__(self, team: Team, author_id: ids.UserId):
        """Initialize management context."""
        if not team.is_member(author_id):
            raise custom_exception.CommentException(
                "Team has not this user"
            )
        self._team = team
        self._author_id = author_id

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionCreateComment(CommentManagement):
    """Class create new comment"""

    def execute(
            self, task_id: ids.TaskId, text: str,
            comment_id: ids.CommentId
    ) -> Comment:
        comment = Comment(
            self._author_id, task_id, text,
            self._team.id,
            comment_id, datetime.now(timezone.utc)
        )
        return comment


