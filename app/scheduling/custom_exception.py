class MeetingsMemberException(Exception):
    """Raise when member.team_id != team.id."""
    pass

class MeetingsManagerException(Exception):
    """Raise when user is not manager."""
    pass

class MeetingOverlapError(Exception):
    """Raised when a meeting overlaps with an existing one."""

class MeetingOrganizerException(Exception):
    """Raise when user has not organizrer's permissions"""
    pass


class MeetingCancelledError(Exception):
    """Raised when a meeting can't cancelled."""
    pass

