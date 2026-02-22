from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

from app.deps.base import get_settings


settings = get_settings()

SCHEMA = "identity"


class UserORM(SQLAlchemyBaseUserTable[int], Base):
    """
    ORM user model for fastapi-users
    """
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_email', 'email'),
        {"schema": SCHEMA} if settings.use_schema else {},
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return f"<UserORM(id={self.id}, email={self.email})>"
