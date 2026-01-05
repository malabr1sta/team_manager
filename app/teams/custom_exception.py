
class MemberNotFoundException(Exception):
    """Raised when a user is not a member of the team."""
    pass

class MemberNotAdminException(Exception):
    """Raised when a member is not at admin of the team."""
    pass

class TeamIdMissingException(Exception):
    """Raised when a team does not have an ID but an operation requires it."""
    pass




