"""sqladmin panel setup."""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqladmin import Admin

from app.admin.auth import AdminAuthBackend
from app.admin import views
from app.deps.base import get_settings


def setup_admin(app: FastAPI, engine: AsyncEngine) -> Admin:
    """Initializes sqladmin and registers model views."""
    settings = get_settings()
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=AdminAuthBackend(
            secret_key=settings.secret_key,
            session_factory=app.state.async_session,
        ),
    )
    admin.add_view(views.UserAdmin)
    admin.add_view(views.TeamAdmin)
    admin.add_view(views.TeamMemberAdmin)
    admin.add_view(views.TeamUserAdmin)
    admin.add_view(views.TaskAdmin)
    admin.add_view(views.TaskCommentAdmin)
    admin.add_view(views.TaskTeamAdmin)
    admin.add_view(views.TaskMemberAdmin)
    admin.add_view(views.TaskUserAdmin)
    admin.add_view(views.EvaluationAdmin)
    admin.add_view(views.EvaluationTaskAdmin)
    admin.add_view(views.EvaluationUserAdmin)
    admin.add_view(views.SchedulingMeetingAdmin)
    admin.add_view(views.SchedulingParticipantAdmin)
    admin.add_view(views.SchedulingTeamAdmin)
    admin.add_view(views.SchedulingMemberAdmin)
    admin.add_view(views.SchedulingUserAdmin)
    admin.add_view(views.CalendarEventAdmin)
    admin.add_view(views.CalendarUserAdmin)
    return admin
