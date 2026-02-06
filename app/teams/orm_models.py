from app.core.database import Base, IdMixin, TimestampMixin

from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
)
from sqlalchemy import String, Integer, ForeignKey


SCHEMA = "teams"
TEAM_FK = f"{SCHEMA}.teams.id" if Base.USE_SCHEMA else "teams.id"
USER_FK = f"{SCHEMA}.teams_user.id" if Base.USE_SCHEMA else "teams_user.id"

TABLE_ARGS = {"schema": SCHEMA} if Base.USE_SCHEMA else {}


class TeamUserOrm(Base, TimestampMixin):
    __tablename__ = 'teams_user'
    __table_args__ = TABLE_ARGS

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


class MemberOrm(Base, IdMixin):
    __tablename__ = 'teams_members'
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(USER_FK)
    )
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(TEAM_FK), nullable=True
    )

    role: Mapped[str] = mapped_column(String)


class TeamOrm(Base, IdMixin, TimestampMixin):

    __tablename__ = 'teams'
    __table_args__ = TABLE_ARGS

    name: Mapped[str] = mapped_column(String)
    members = relationship(
        MemberOrm,
        foreign_keys="MemberOrm.team_id",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
