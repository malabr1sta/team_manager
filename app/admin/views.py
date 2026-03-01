"""sqladmin model views."""

from sqladmin import ModelView

from app.calendar.orm_models import CalendarEventOrm, CalendarUserOrm
from app.evaluations.orm_models import EvaluationOrm, EvaluationTaskOrm, EvaluationUserOrm
from app.identity.orm_models import UserORM
from app.scheduling.orm_models import (
    SchedulingMeetingOrm,
    SchedulingMeetingParticipantOrm,
    SchedulingMemberOrm,
    SchedulingTeamOrm,
    SchedulingUserOrm,
)
from app.tasks.orm_models import CommentOrm, TaskMemberOrm, TaskOrm, TaskTeamOrm, TaskUserOrm
from app.teams.orm_models import MemberOrm, TeamOrm, TeamUserOrm

IDENTITY_CATEGORY = "Identity"
TEAMS_CATEGORY = "Teams"
TASKS_CATEGORY = "Tasks"
EVALUATIONS_CATEGORY = "Evaluations"
SCHEDULING_CATEGORY = "Scheduling"
CALENDAR_CATEGORY = "Calendar"


class UserAdmin(ModelView, model=UserORM):
    """Admin view for identity users."""

    category = IDENTITY_CATEGORY
    column_list = [
        "id",
        "email",
        "username",
        "is_superuser",
        "is_active",
        "deleted",
    ]
    column_searchable_list = ["email", "username"]
    column_sortable_list = ["id", "email"]
    form_excluded_columns = ["hashed_password"]
    can_create = False
    can_edit = True
    can_delete = False


class TeamAdmin(ModelView, model=TeamOrm):
    """Admin view for teams."""

    category = TEAMS_CATEGORY
    column_list = [TeamOrm.id, TeamOrm.name]
    column_searchable_list = [TeamOrm.name]
    column_sortable_list = [TeamOrm.id, TeamOrm.name]
    can_create = False
    can_edit = True
    can_delete = False


class TeamMemberAdmin(ModelView, model=MemberOrm):
    """Admin view for team members."""

    category = TEAMS_CATEGORY
    column_list = [MemberOrm.id, MemberOrm.team_id, MemberOrm.user_id, MemberOrm.role]
    column_searchable_list = [MemberOrm.role]
    column_sortable_list = [MemberOrm.id, MemberOrm.team_id, MemberOrm.user_id]
    can_create = False
    can_edit = True
    can_delete = False


class TeamUserAdmin(ModelView, model=TeamUserOrm):
    """Admin view for team users."""

    category = TEAMS_CATEGORY
    column_list = [TeamUserOrm.id, TeamUserOrm.username]
    column_searchable_list = [TeamUserOrm.username]
    column_sortable_list = [TeamUserOrm.id, TeamUserOrm.username]
    can_create = False
    can_edit = False
    can_delete = False


class TaskAdmin(ModelView, model=TaskOrm):
    """Admin view for tasks."""

    category = TASKS_CATEGORY
    column_list = [
        TaskOrm.id,
        TaskOrm.team_id,
        TaskOrm.supervisor_id,
        TaskOrm.executor_id,
        TaskOrm.title,
        TaskOrm.status,
        TaskOrm.deadline,
        TaskOrm.deleted,
    ]
    column_searchable_list = [TaskOrm.title, TaskOrm.description]
    column_sortable_list = [TaskOrm.id, TaskOrm.team_id, TaskOrm.deadline]
    can_create = False
    can_edit = True
    can_delete = False


class TaskCommentAdmin(ModelView, model=CommentOrm):
    """Admin view for task comments."""

    category = TASKS_CATEGORY
    column_list = [CommentOrm.id, CommentOrm.task_id, CommentOrm.author_id, CommentOrm.text]
    column_searchable_list = [CommentOrm.text]
    column_sortable_list = [CommentOrm.id, CommentOrm.task_id, CommentOrm.author_id]
    can_create = False
    can_edit = True
    can_delete = False


class TaskTeamAdmin(ModelView, model=TaskTeamOrm):
    """Admin view for task teams."""

    category = TASKS_CATEGORY
    column_list = [TaskTeamOrm.id]
    column_sortable_list = [TaskTeamOrm.id]
    can_create = False
    can_edit = False
    can_delete = False


class TaskMemberAdmin(ModelView, model=TaskMemberOrm):
    """Admin view for task members."""

    category = TASKS_CATEGORY
    column_list = [TaskMemberOrm.id, TaskMemberOrm.team_id, TaskMemberOrm.user_id, TaskMemberOrm.role]
    column_searchable_list = [TaskMemberOrm.role]
    column_sortable_list = [TaskMemberOrm.id, TaskMemberOrm.team_id, TaskMemberOrm.user_id]
    can_create = False
    can_edit = False
    can_delete = False


class TaskUserAdmin(ModelView, model=TaskUserOrm):
    """Admin view for task users."""

    category = TASKS_CATEGORY
    column_list = [TaskUserOrm.id, TaskUserOrm.username]
    column_searchable_list = [TaskUserOrm.username]
    column_sortable_list = [TaskUserOrm.id, TaskUserOrm.username]
    can_create = False
    can_edit = False
    can_delete = False


class EvaluationAdmin(ModelView, model=EvaluationOrm):
    """Admin view for evaluations."""

    category = EVALUATIONS_CATEGORY
    column_list = [EvaluationOrm.id, EvaluationOrm.user_id, EvaluationOrm.team_id, EvaluationOrm.task_id, EvaluationOrm.grade]
    column_sortable_list = [EvaluationOrm.id, EvaluationOrm.user_id, EvaluationOrm.team_id]
    can_create = False
    can_edit = True
    can_delete = False


class EvaluationTaskAdmin(ModelView, model=EvaluationTaskOrm):
    """Admin view for evaluation tasks."""

    category = EVALUATIONS_CATEGORY
    column_list = [
        EvaluationTaskOrm.id,
        EvaluationTaskOrm.team_id,
        EvaluationTaskOrm.supervisor_id,
        EvaluationTaskOrm.executor_id,
        EvaluationTaskOrm.status,
    ]
    column_sortable_list = [EvaluationTaskOrm.id, EvaluationTaskOrm.team_id]
    can_create = False
    can_edit = False
    can_delete = False


class EvaluationUserAdmin(ModelView, model=EvaluationUserOrm):
    """Admin view for evaluation users."""

    category = EVALUATIONS_CATEGORY
    column_list = [EvaluationUserOrm.id, EvaluationUserOrm.username]
    column_searchable_list = [EvaluationUserOrm.username]
    column_sortable_list = [EvaluationUserOrm.id, EvaluationUserOrm.username]
    can_create = False
    can_edit = False
    can_delete = False


class SchedulingMeetingAdmin(ModelView, model=SchedulingMeetingOrm):
    """Admin view for meetings."""

    category = SCHEDULING_CATEGORY
    column_list = [
        SchedulingMeetingOrm.id,
        SchedulingMeetingOrm.team_id,
        SchedulingMeetingOrm.organizer_id,
        SchedulingMeetingOrm.start,
        SchedulingMeetingOrm.end,
        SchedulingMeetingOrm.is_cancelled,
    ]
    column_searchable_list = [SchedulingMeetingOrm.description]
    column_sortable_list = [SchedulingMeetingOrm.id, SchedulingMeetingOrm.team_id, SchedulingMeetingOrm.start]
    can_create = False
    can_edit = True
    can_delete = False


class SchedulingParticipantAdmin(ModelView, model=SchedulingMeetingParticipantOrm):
    """Admin view for meeting participants."""

    category = SCHEDULING_CATEGORY
    column_list = [
        SchedulingMeetingParticipantOrm.id,
        SchedulingMeetingParticipantOrm.meeting_id,
        SchedulingMeetingParticipantOrm.user_id,
    ]
    column_sortable_list = [SchedulingMeetingParticipantOrm.id, SchedulingMeetingParticipantOrm.meeting_id]
    can_create = False
    can_edit = False
    can_delete = False


class SchedulingTeamAdmin(ModelView, model=SchedulingTeamOrm):
    """Admin view for scheduling teams."""

    category = SCHEDULING_CATEGORY
    column_list = [SchedulingTeamOrm.id]
    column_sortable_list = [SchedulingTeamOrm.id]
    can_create = False
    can_edit = False
    can_delete = False


class SchedulingMemberAdmin(ModelView, model=SchedulingMemberOrm):
    """Admin view for scheduling members."""

    category = SCHEDULING_CATEGORY
    column_list = [
        SchedulingMemberOrm.id,
        SchedulingMemberOrm.team_id,
        SchedulingMemberOrm.user_id,
        SchedulingMemberOrm.is_manager,
    ]
    column_sortable_list = [SchedulingMemberOrm.id, SchedulingMemberOrm.team_id, SchedulingMemberOrm.user_id]
    can_create = False
    can_edit = False
    can_delete = False


class SchedulingUserAdmin(ModelView, model=SchedulingUserOrm):
    """Admin view for scheduling users."""

    category = SCHEDULING_CATEGORY
    column_list = [SchedulingUserOrm.id, SchedulingUserOrm.username]
    column_searchable_list = [SchedulingUserOrm.username]
    column_sortable_list = [SchedulingUserOrm.id, SchedulingUserOrm.username]
    can_create = False
    can_edit = False
    can_delete = False


class CalendarEventAdmin(ModelView, model=CalendarEventOrm):
    """Admin view for calendar events."""

    category = CALENDAR_CATEGORY
    column_list = [
        CalendarEventOrm.id,
        CalendarEventOrm.user_id,
        CalendarEventOrm.event_type,
        CalendarEventOrm.title,
        CalendarEventOrm.time,
        CalendarEventOrm.reference_id,
        CalendarEventOrm.cancelled,
    ]
    column_searchable_list = [CalendarEventOrm.title, CalendarEventOrm.description]
    column_sortable_list = [CalendarEventOrm.id, CalendarEventOrm.user_id, CalendarEventOrm.time]
    can_create = False
    can_edit = False
    can_delete = False


class CalendarUserAdmin(ModelView, model=CalendarUserOrm):
    """Admin view for calendar users."""

    category = CALENDAR_CATEGORY
    column_list = [CalendarUserOrm.id, CalendarUserOrm.username]
    column_searchable_list = [CalendarUserOrm.username]
    column_sortable_list = [CalendarUserOrm.id, CalendarUserOrm.username]
    can_create = False
    can_edit = False
    can_delete = False
