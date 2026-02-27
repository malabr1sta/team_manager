from sqlalchemy import delete, select

from app.core.custom_types import ids
from app.core.repositories.base import AbstractRepository
from app.scheduling import mappers, models, orm_models


class SQLAlchemySchedulingUserRepository(AbstractRepository[models.User]):
    async def get_by_id(self, id: int) -> models.User | None:
        result = await self.session.execute(
            select(orm_models.SchedulingUserOrm).where(
                orm_models.SchedulingUserOrm.id == id
            )
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            return None

        user = mappers.SchedulingUserMapper.to_domain(user_orm)
        participant_rows = await self.session.execute(
            select(orm_models.SchedulingMeetingParticipantOrm).where(
                orm_models.SchedulingMeetingParticipantOrm.user_id == id
            )
        )
        meeting_ids = [row.meeting_id for row in participant_rows.scalars().all()]
        meetings: list[models.Meeting] = []
        for meeting_id in meeting_ids:
            meeting = await SQLAlchemySchedulingMeetingRepository(self.uow).get_by_id(
                meeting_id
            )
            if meeting is not None:
                meetings.append(meeting)
        user._meetings = meetings
        return user

    async def save(self, domain: models.User) -> None:
        result = await self.session.execute(
            select(orm_models.SchedulingUserOrm).where(
                orm_models.SchedulingUserOrm.id == domain.id
            )
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            self.session.add(mappers.SchedulingUserMapper.to_orm(domain))
            return
        mappers.SchedulingUserMapper.update_orm(user_orm, domain)


class SQLAlchemySchedulingTeamRepository(AbstractRepository[models.Team]):
    async def get_by_id(self, id: int) -> models.Team | None:
        team_result = await self.session.execute(
            select(orm_models.SchedulingTeamOrm).where(
                orm_models.SchedulingTeamOrm.id == id
            )
        )
        team_orm = team_result.scalar_one_or_none()
        if team_orm is None:
            return None
        member_result = await self.session.execute(
            select(orm_models.SchedulingMemberOrm).where(
                orm_models.SchedulingMemberOrm.team_id == id
            )
        )
        members_orm = member_result.scalars().all()
        return mappers.SchedulingTeamMapper.to_domain(team_orm, members_orm)

    async def save(self, domain: models.Team) -> None:
        result = await self.session.execute(
            select(orm_models.SchedulingTeamOrm).where(
                orm_models.SchedulingTeamOrm.id == domain.id
            )
        )
        team_orm = result.scalar_one_or_none()
        if team_orm is None:
            self.session.add(mappers.SchedulingTeamMapper.to_orm(domain))
        await self.session.execute(
            delete(orm_models.SchedulingMemberOrm).where(
                orm_models.SchedulingMemberOrm.team_id == domain.id
            )
        )
        for member in domain.members:
            self.session.add(mappers.SchedulingMemberMapper.to_orm(member))


class SQLAlchemySchedulingMemberRepository(AbstractRepository[models.MemberTeam]):
    async def get_by_user_and_team(
            self, user_id: int, team_id: int
    ) -> models.MemberTeam | None:
        result = await self.session.execute(
            select(orm_models.SchedulingMemberOrm).where(
                orm_models.SchedulingMemberOrm.user_id == user_id,
                orm_models.SchedulingMemberOrm.team_id == team_id,
            )
        )
        member_orm = result.scalar_one_or_none()
        if member_orm is None:
            return None
        return mappers.SchedulingMemberMapper.to_domain(member_orm)

    async def save(self, domain: models.MemberTeam) -> None:
        result = await self.session.execute(
            select(orm_models.SchedulingMemberOrm).where(
                orm_models.SchedulingMemberOrm.user_id == domain.user_id,
                orm_models.SchedulingMemberOrm.team_id == domain.team_id,
            )
        )
        member_orm = result.scalar_one_or_none()
        if member_orm is None:
            self.session.add(mappers.SchedulingMemberMapper.to_orm(domain))
            return
        mappers.SchedulingMemberMapper.update_orm(member_orm, domain)

    async def delete(self, user_id: int, team_id: int) -> None:
        await self.session.execute(
            delete(orm_models.SchedulingMemberOrm).where(
                orm_models.SchedulingMemberOrm.user_id == user_id,
                orm_models.SchedulingMemberOrm.team_id == team_id,
            )
        )


class SQLAlchemySchedulingMeetingRepository(AbstractRepository[models.Meeting]):
    async def get_by_id(self, id: int) -> models.Meeting | None:
        result = await self.session.execute(
            select(orm_models.SchedulingMeetingOrm).where(
                orm_models.SchedulingMeetingOrm.id == id
            )
        )
        meeting_orm = result.scalar_one_or_none()
        if meeting_orm is None:
            return None
        participants_result = await self.session.execute(
            select(orm_models.SchedulingMeetingParticipantOrm).where(
                orm_models.SchedulingMeetingParticipantOrm.meeting_id == id
            )
        )
        participants = participants_result.scalars().all()
        return mappers.SchedulingMeetingMapper.to_domain(meeting_orm, participants)

    async def get_by_team(self, team_id: int) -> list[models.Meeting]:
        result = await self.session.execute(
            select(orm_models.SchedulingMeetingOrm).where(
                orm_models.SchedulingMeetingOrm.team_id == team_id
            )
        )
        meetings = result.scalars().all()
        items: list[models.Meeting] = []
        for meeting_orm in meetings:
            participants_result = await self.session.execute(
                select(orm_models.SchedulingMeetingParticipantOrm).where(
                    orm_models.SchedulingMeetingParticipantOrm.meeting_id
                    == meeting_orm.id
                )
            )
            participants = participants_result.scalars().all()
            items.append(
                mappers.SchedulingMeetingMapper.to_domain(meeting_orm, participants)
            )
        return items

    async def save(self, domain: models.Meeting) -> None:
        result = await self.session.execute(
            select(orm_models.SchedulingMeetingOrm).where(
                orm_models.SchedulingMeetingOrm.id == domain.id
            )
        )
        meeting_orm = result.scalar_one_or_none()
        if meeting_orm is None:
            meeting_orm = mappers.SchedulingMeetingMapper.to_orm(domain)
            self.session.add(meeting_orm)
            await self.session.flush()
            domain._id = ids.MeetingId(meeting_orm.id)
            domain.mark_created_event()
        else:
            mappers.SchedulingMeetingMapper.update_orm(meeting_orm, domain)

        if domain.id is None:
            raise ValueError("meeting id is required after save")
        await self.session.execute(
            delete(orm_models.SchedulingMeetingParticipantOrm).where(
                orm_models.SchedulingMeetingParticipantOrm.meeting_id == domain.id
            )
        )
        for participant in domain.participants:
            if participant is None:
                continue
            meeting_participant = models.MeetingParticipant(
                user_id=participant.user_id,
                meeting_id=domain.id,
            )
            self.session.add(
                mappers.SchedulingMeetingParticipantMapper.to_orm(meeting_participant)
            )
        self.uow._seen.add(domain)
