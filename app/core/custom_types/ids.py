from typing import NewType, TypeVar, Literal


ID = TypeVar("ID")

UserId = NewType("UserId", int)
TeamId = NewType("TeamId", int)
TaskId = NewType("TaskId", int)
MeetingId = NewType("MeetingId", int)

Grade = Literal[1, 2, 3, 4, 5]
CommentId = NewType("CommentId", int)
