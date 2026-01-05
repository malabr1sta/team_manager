
class UserDeleteException(Exception):
    """
    Exception raised when an operation on a User fails due to deletion state.

    Use this to indicate that the user cannot perform the requested action
    because it has been deleted or marked as deleted.
    """
    pass

