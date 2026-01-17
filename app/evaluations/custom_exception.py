class EvaluationException(Exception):
    """Raise when task status is not done"""
    pass

class EvaluationSupervisorException(Exception):
    """Raise when user has not supervisor's permissions"""
    pass
