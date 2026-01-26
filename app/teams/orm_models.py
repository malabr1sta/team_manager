from app.core.database import Base, IdMixin

from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
)
from sqlalchemy import DateTime, String, func, Integer, ForeignKey


SCHEMA = "teams"
TEAM_FK = f"{SCHEMA}.teams.id" if Base.USE_SCHEMA else "teams.id"
TABLE_ARGS = {"schema": SCHEMA} if Base.USE_SCHEMA else {}


class MemberOrm(Base, IdMixin):

    __tablename__ = 'members'
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(Integer)
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(TEAM_FK), nullable=True
    )

    role: Mapped[str] = mapped_column(String)


class TeamOrm(Base, IdMixin):

    __tablename__ = 'teams'
    __table_args__ = TABLE_ARGS

    name: Mapped[str] = mapped_column(String)
    members = relationship(
        MemberOrm,
        lazy="joined",
        cascade="all, delete-orphan"
    )
