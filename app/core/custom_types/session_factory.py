from typing import Callable, AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession


AsyncSessionFactory = Callable[[], AsyncContextManager[AsyncSession]]
