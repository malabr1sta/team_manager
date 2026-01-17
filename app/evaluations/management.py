from app.core.custom_types import ids, grade
from app.evaluations import models, custom_exception


def create_evaluation(
    supervisor_id: ids.UserId,
    task: models.Task,
    grade: grade.Grade
) -> models.Evaluation:

    if supervisor_id != task.supervisor_id:
        raise custom_exception.EvaluationSupervisorException(
            "user is not supervisor this task"
        )

    return task.create_evaluation(grade)
