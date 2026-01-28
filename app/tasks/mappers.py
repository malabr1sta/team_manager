from app.tasks.orm_models import (
    TaskUserOrm,
    TaskMemberOrm
)
from app.core.custom_types import ids, role
from app.tasks.models import (
    TaskUser,
    MemberTask
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

