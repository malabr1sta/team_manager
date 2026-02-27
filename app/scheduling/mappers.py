from collections.abc import Sequence

from app.core.custom_types import ids
from app.scheduling import models, orm_models


class SchedulingUserMapper:
    @staticmethod
    def to_domain(orm: orm_models.SchedulingUserOrm) -> models.User:
        return models.User(
            id=ids.UserId(orm.id),
            username=orm.username or "",
        )

    @staticmethod
    def to_orm(user: models.User) -> orm_models.SchedulingUserOrm:
        return orm_models.SchedulingUserOrm(
            id=user.id,
            username=user.username,
        )

    @staticmethod
    def update_orm(orm: orm_models.SchedulingUserOrm, user: models.User) -> None:
        orm.username = user.username


class SchedulingMemberMapper:
    @staticmethod
    def to_domain(orm: orm_models.SchedulingMemberOrm) -> models.MemberTeam:
        return models.MemberTeam(
            user_id=ids.UserId(orm.user_id),
            team_id=ids.TeamId(orm.team_id),
            is_manager=orm.is_manager,
        )

    @staticmethod
    def to_orm(member: models.MemberTeam) -> orm_models.SchedulingMemberOrm:
        return orm_models.SchedulingMemberOrm(
            user_id=member.user_id,
            team_id=member.team_id,
            is_manager=member.is_manager,
        )

    @staticmethod
    def update_orm(
            orm: orm_models.SchedulingMemberOrm,
            member: models.MemberTeam,
    ) -> None:
        orm.user_id = member.user_id
        orm.team_id = member.team_id
        orm.is_manager = member.is_manager


class SchedulingTeamMapper:
    @staticmethod
    def to_domain(
            orm: orm_models.SchedulingTeamOrm,
            members: Sequence[orm_models.SchedulingMemberOrm],
    ) -> models.Team:
        return models.Team(
            id=ids.TeamId(orm.id),
            members=[SchedulingMemberMapper.to_domain(member) for member in members],
        )

    @staticmethod
    def to_orm(team: models.Team) -> orm_models.SchedulingTeamOrm:
        return orm_models.SchedulingTeamOrm(id=team.id)


class SchedulingMeetingParticipantMapper:
    @staticmethod
    def to_domain(
            orm: orm_models.SchedulingMeetingParticipantOrm
    ) -> models.MeetingParticipant:
        return models.MeetingParticipant(
            user_id=ids.UserId(orm.user_id),
            meeting_id=ids.MeetingId(orm.meeting_id),
        )

    @staticmethod
    def to_orm(
            participant: models.MeetingParticipant
    ) -> orm_models.SchedulingMeetingParticipantOrm:
        if participant.meeting_id is None:
            raise ValueError("meeting_id is required for participant persistence")
        return orm_models.SchedulingMeetingParticipantOrm(
            user_id=participant.user_id,
            meeting_id=participant.meeting_id,
        )


class SchedulingMeetingMapper:
    @staticmethod
    def to_domain(
            orm: orm_models.SchedulingMeetingOrm,
            participants: Sequence[orm_models.SchedulingMeetingParticipantOrm],
    ) -> models.Meeting:
        return models.Meeting(
            id=ids.MeetingId(orm.id),
            organizer_id=ids.UserId(orm.organizer_id),
            team_id=ids.TeamId(orm.team_id),
            start=orm.start,
            end=orm.end,
            description=orm.description,
            is_cancelled=orm.is_cancelled,
            participants=[
                SchedulingMeetingParticipantMapper.to_domain(item)
                for item in participants
            ],
        )

    @staticmethod
    def to_orm(meeting: models.Meeting) -> orm_models.SchedulingMeetingOrm:
        return orm_models.SchedulingMeetingOrm(
            id=meeting.id,
            organizer_id=meeting.organizer_id,
            team_id=meeting.team_id,
            start=meeting.start,
            end=meeting.end,
            description=meeting.description,
            is_cancelled=meeting.is_cancelled,
        )

    @staticmethod
    def update_orm(
            orm: orm_models.SchedulingMeetingOrm,
            meeting: models.Meeting,
    ) -> None:
        orm.organizer_id = meeting.organizer_id
        orm.team_id = meeting.team_id
        orm.start = meeting.start
        orm.end = meeting.end
        orm.description = meeting.description
        orm.is_cancelled = meeting.is_cancelled
