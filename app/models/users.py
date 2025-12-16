from app.database import Base
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

import enum


class RoleEnum(str, enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(Base):

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SqlEnum(RoleEnum, name="role"),
        default=RoleEnum.user,
        nullable=False
    )
