"""CLI script to create or promote a superuser."""

from __future__ import annotations

import argparse
import asyncio

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.deps.base import get_settings
from app.identity.orm_models import UserORM


def _database_url() -> str:
    settings = get_settings()
    return (
        f"postgresql+asyncpg://{settings.database_user}:"
        f"{settings.database_password}@"
        f"{settings.database_host}:{settings.database_port}/"
        f"{settings.database_name}"
    )


async def _create_or_promote_superuser(
    email: str,
    password: str,
    username: str,
) -> None:
    hasher = PasswordHash.recommended()
    engine = create_async_engine(_database_url(), echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.email == email)
            )
            user = result.scalar_one_or_none()

            if user is None:
                user = UserORM(
                    email=email,
                    hashed_password=hasher.hash(password),
                    is_active=True,
                    is_superuser=True,
                    is_verified=True,
                    username=username,
                    deleted=False,
                )
                session.add(user)
                await session.commit()
                print(f"Created superuser: {email}")
                return

            user.username = username
            user.hashed_password = hasher.hash(password)
            user.is_active = True
            user.is_superuser = True
            user.is_verified = True
            user.deleted = False
            await session.commit()
            print(f"Promoted existing user to superuser: {email}")
    finally:
        await engine.dispose()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or promote a superuser for sqladmin."
    )
    parser.add_argument("--email", required=True, help="Superuser email")
    parser.add_argument("--password", required=True, help="Superuser password")
    parser.add_argument("--username", required=True, help="Superuser username")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    asyncio.run(
        _create_or_promote_superuser(
            email=args.email.strip().lower(),
            password=args.password,
            username=args.username.strip(),
        )
    )


if __name__ == "__main__":
    main()
