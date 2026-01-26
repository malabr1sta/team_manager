from enum import Enum

class CalendarEventType(str, Enum):
    MEETING = "meeting"
    TASK = "task"

