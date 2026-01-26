from app.teams.orm_models import MemberOrm, TeamOrm
from app.core.custom_types import ids, role
from app.teams.models import Member, Team


class MemberMapper:

    @staticmethod
    def to_domain(orm: MemberOrm) -> Member:
        """ORM -> Domain"""
        team_id = ids.TeamId(orm.team_id) if orm.team_id is not None else None
        return Member(
            user_id=ids.UserId(orm.user_id),
            team_id=team_id,
            role=role.UserRole(orm.role)
        )

    @staticmethod
    def to_orm(member: Member) -> MemberOrm:
        """Domain -> ORM"""
        return MemberOrm(
            user_id=member.user_id,
            team_id=member.team_id,
            role=member.role
        )

    @staticmethod
    def update_orm(orm: MemberOrm, member: Member) -> None:
        """Updating an existing ORM model"""
        orm.user_id=member.user_id
        orm.team_id=member.team_id
        orm.role=member.role


class TeamMapper:

    @staticmethod
    def to_domain(orm: TeamOrm) -> Team:
        """ORM -> Domain"""
        members = [
            Member(
                user_id=ids.UserId(member.user_id),
                team_id=member.team_id,
                role=role.UserRole(member.role)
            )
            for member in orm.members
        ]
        return Team(
            id=ids.TeamId(orm.id),
            members=members,
            name=orm.name
        )

    @staticmethod
    def to_orm(team: Team) -> TeamOrm:
        """Domain -> ORM"""
        team_orm = TeamOrm(
            id=team.id,
            name=team._name
        )

        for member in team.members:
            member_model = MemberOrm(
                user_id=member.user_id,
                team_id=member.team_id,
                role=member.role.value
            )
            team_orm.members.append(member_model)

        return team_orm

    @staticmethod
    def update_orm(team_orm: TeamOrm, team: Team) -> None:
        """Updating an existing ORM model"""
        team_orm.name = team._name

        team_orm.members.clear()
        for member in team.members:
            member_model = MemberOrm(
                team_id=team_orm.id,
                user_id=member.user_id,
                role=member.role
            )
            team_orm.members.append(member_model)
