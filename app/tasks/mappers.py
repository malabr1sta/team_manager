from app.tasks.orm_models import (
    TaskUserOrm,
    TaskMemberOrm,
    TaskTeamOrm,
    CommentOrm,
    TaskOrm
)
from app.core.custom_types import ids, role
from app.tasks.models import (
    TaskUser,
    MemberTask,
    Team,
    Comment,
    Task
)

class TaskUserMapper:

    @staticmethod
    def to_domain(orm: TaskUserOrm) -> TaskUser:
        return TaskUser(ids.UserId(orm.id), orm.username)

    @staticmethod
    def to_orm(user: TaskUser) -> TaskUserOrm:
        return TaskUserOrm(
            id=user.id, username=user.username
        )

    @staticmethod
    def update_orm(orm: TaskUserOrm, user: TaskUser) -> None:
        orm.id=user.id
        orm.username = user.username


class TaskMemberMapper:

    @staticmethod
    def to_domain(orm: TaskMemberOrm) -> MemberTask:
        """ORM -> Domain"""
        return MemberTask(
            user_id=ids.UserId(orm.user_id),
            team_id=ids.TeamId(orm.team_id),
            role=role.UserTaskRole(orm.role)
        )

    @staticmethod
    def to_orm(member: MemberTask) -> TaskMemberOrm:
        """Domain -> ORM"""
        return TaskMemberOrm(
            user_id=member.user_id,
            team_id=member.team_id,
            role=member.role
        )

    @staticmethod
    def update_orm(orm: TaskMemberOrm, member: MemberTask) -> None:
        """Updating an existing ORM model"""
        orm.user_id=member.user_id
        orm.team_id=member.team_id
        orm.role=member.role


class TaskTeamMapper:

    @staticmethod
    def to_domain(orm: TaskTeamOrm) -> Team:
        """ORM -> Domain"""
        members = [
            MemberTask(
                user_id=ids.UserId(member.user_id),
                team_id=member.team_id,
                role=role.UserTaskRole(member.role)
            )
            for member in orm.members
        ]
        return Team(
            id=ids.TeamId(orm.id),
            members=members,
        )

    @staticmethod
    def to_orm(team: Team) -> TaskTeamOrm:
        """Domain -> ORM"""
        members_orm = [
            TaskMemberOrm(
                user_id=member.user_id,
                team_id=member.team_id,
                role=member.role
            )
            for member in team.members
        ]

        team_orm = TaskTeamOrm(
            id=team.id,
            members=members_orm
        )

        return team_orm


    @staticmethod
    def update_orm(team_orm: TaskTeamOrm, team: Team) -> None:
        """Updating an existing ORM model"""

        team_orm.members.clear()
        for member in team.members:
            member_model = TaskMemberOrm(
                team_id=team_orm.id,
                user_id=member.user_id,
                role=member.role
            )
            team_orm.members.append(member_model)


class TaskCommentMapper:

    @staticmethod
    def to_domain(orm: CommentOrm) -> Comment:
        """ORM -> Domain"""
        return Comment(
            id=ids.CommentId(orm.id),
            author_id=ids.UserId(orm.author_id),
            task_id=ids.TaskId(orm.task_id),
            text=orm.text,
            created_at=orm.created_dttm
        )


    @staticmethod
    def to_orm(comment: Comment) -> CommentOrm:
        """Domain -> ORM"""
        return CommentOrm(
            author_id=comment.author_id,
            task_id=comment.task_id,
            text=comment.text,
        )

    @staticmethod
    def update_orm(orm: CommentOrm, comment: Comment) -> None:
        """Updating an existing ORM model"""
        orm.text = comment.text


class TaskMapper:

    @staticmethod
    def to_domain(orm: TaskOrm) -> Task:
        """ORM -> Domain"""
        executor_id = ids.UserId(orm.executor_id) if orm.executor_id else None
        task = Task(
            id=ids.TaskId(orm.id),
            team_id=ids.TeamId(orm.team_id) if orm.team_id else None,
            supervisor_id=ids.UserId(orm.supervisor_id),
            executor_id=executor_id,
            description=orm.description,
            title=orm.title,
            deadline=orm.deadline,
            status=orm.status,
            created_at=orm.created_dttm,
            updated_at=orm.updated_dttm,
        )
        task._deleted = orm.deleted
        return task

    @staticmethod
    def to_orm(task: Task) -> TaskOrm:
        """Domain -> ORM"""
        return TaskOrm(
            team_id=task.team_id,
            supervisor_id=task.supervisor_id,
            executor_id=task.executor_id,
            description=task.description,
            title=task.title,
            deadline=task.deadline,
            status=task.status,
            deleted=task.deleted,
        )

    @staticmethod
    def update_orm(orm: TaskOrm, task: Task) -> None:
        """Updating an existing ORM model"""
        orm.team_id=task.team_id
        orm.supervisor_id=task.supervisor_id
        orm.executor_id=task.executor_id
        orm.description=task.description
        orm.title=task.title
        orm.deadline=task._deadline
        orm.status=task.status
        orm.deleted=task.deleted
