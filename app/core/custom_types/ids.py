from typing import NewType, TypeVar


ID = TypeVar("ID")

UserId = NewType("UserId", int)
TeamId = NewType("TeamId", int)
TaskId = NewType("TaskId", int)
CommentId = NewType("CommentId", int)
