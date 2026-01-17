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

