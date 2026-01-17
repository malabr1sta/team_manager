from typing import TypedDict
from app.core.custom_types import task_status


class TaskUpdateArgs(TypedDict, total=False):
    title: str
    description: str
    status: task_status.TaskStatus
    deleted: bool
