class TaskDeadlineException(Exception):
    """The deadline can't be in the past."""
    pass

class TaskMemberException(Exception):
    """Raise when member.team_id != team.id or role != MEMBER."""
    pass

class TaskSupervisorException(Exception):
    """Raise when user has not supervisor's permissions"""
    pass

class CommentException(Exception):
    """Raise when user has not permissions for comments"""
    pass

class TaskMemberNotFoundException(Exception):
    """Raised when a user is not a member of the team."""
    pass

class TaskMemberNotAdminException(Exception):
    """Raised when a member is not at admin of the team."""
    pass

class TaskTeamIdMissingException(Exception):
    """Raised when a team does not have an ID but an operation requires it."""
    pass

class TeamNotFoundException(Exception):
    """Raised when a team not found"""
