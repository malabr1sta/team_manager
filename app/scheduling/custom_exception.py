class MeetingsMemberException(Exception):
    """Raise when member.team_id != team.id."""
    pass

class MeetingOverlapError(Exception):
    """Raised when a meeting overlaps with an existing one."""

class MeetingCancelledError(Exception):
    """Raised when a meeting can't cancelled."""

