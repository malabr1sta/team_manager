import pytest
from datetime import datetime
from sqlalchemy import select

from app.tasks import (
    models,
    orm_models,
    repository
)
from app.core.custom_types import ids, role


@pytest.mark.anyio
async def test_save_creates_new_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskUserOrm)
        .where(orm_models.TaskUserOrm.id == 1)
    )
    orm_user = result.scalar_one()

    assert orm_user.id == 1
    assert orm_user.username == "leonya"


@pytest.mark.anyio
async def test_get_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    user_1 = await repo.get_by_id(1)

    assert user_1
    assert user_1.id == 1
    assert user_1.username == "leonya"


@pytest.mark.anyio
async def test_save_creates_new_member(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)
    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskMemberOrm)
        .where(
            orm_models.TaskMemberOrm.user_id == 1,
            orm_models.TaskMemberOrm.team_id == 1
        )
    )
    orm_member = result.scalar_one()

    assert orm_member.user_id == 1
    assert orm_member.team_id == 1
    assert orm_member.role == role.UserTaskRole.MEMBER


@pytest.mark.anyio
async def test_save_updates_existing_member(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    same_member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(same_member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskMemberOrm)
        .where(
            orm_models.TaskMemberOrm.user_id == 1,
            orm_models.TaskMemberOrm.team_id == 1,
            orm_models.TaskMemberOrm.role == role.UserTaskRole.MEMBER
        )
    )
    all_members = result.scalars().all()
    assert len(all_members) == 1


@pytest.mark.anyio
async def test_save_creates_multiple_roles_for_same_user_and_team(async_session):
    """We check that a user can have multiple roles in one team"""
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    await repo.save(member1)

    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MANAGER
    )
    await repo.save(member2)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 2
    roles = {member.role for member in members}
    assert roles == {role.UserTaskRole.MEMBER, role.UserTaskRole.MANAGER}


@pytest.mark.anyio
async def test_get_by_user_returns_all_roles(async_session):
    """We check that get_by_user returns all user roles in all commands"""
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MANAGER
    )
    member3 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member1)
    await repo.save(member2)
    await repo.save(member3)
    await async_session.commit()

    members = await repo.get_by_user(1)

    assert len(members) == 3


@pytest.mark.anyio
async def test_get_by_user(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MANAGER
    )

    await repo.save(member1)
    await repo.save(member2)
    await async_session.commit()

    members = await repo.get_by_user(1)

    assert len(members) == 2
    assert all(member.user_id == 1 for member in members)
    team_ids = {member.team_id for member in members}
    assert team_ids == {1, 2}


@pytest.mark.anyio
async def test_get_by_user_empty_result(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    members = await repo.get_by_user(999)

    assert members == []


@pytest.mark.anyio
async def test_get_by_user_and_team(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 1
    assert members[0].user_id == 1
    assert members[0].team_id == 1
    assert members[0].role == role.UserTaskRole.MEMBER


@pytest.mark.anyio
async def test_get_by_user_and_team_empty_result(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 999)

    assert members == []


@pytest.mark.anyio
async def test_get_by_user_and_team_filters_correctly(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MANAGER
    )
    member3 = models.MemberTask(
        user_id=ids.UserId(2),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member1)
    await repo.save(member2)
    await repo.save(member3)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 1
    assert members[0].user_id == 1
    assert members[0].team_id == 1


@pytest.mark.anyio
async def test_save_creates_new_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)
    team = models.Team(
        id=ids.TeamId(100),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    orm_team = result.scalar_one()

    assert orm_team.id == 100


@pytest.mark.anyio
async def test_save_updates_existing_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(100),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    updated_team = models.Team(
        id=ids.TeamId(100),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(100),
                role=role.UserTaskRole.MEMBER
            )
        ]
    )

    await repo.save(updated_team)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    orm_team = result.scalar_one()

    assert orm_team.id == 100

    result_all = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    all_teams = result_all.scalars().all()
    assert len(all_teams) == 1


@pytest.mark.anyio
async def test_get_by_id_returns_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(200),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(200),
                role=role.UserTaskRole.MANAGER
            )
        ]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(200)

    assert found_team is not None
    assert found_team.id == 200
    assert len(found_team.members) == 1
    assert found_team.members[0].user_id == 1
    assert found_team.members[0].role == role.UserTaskRole.MANAGER


@pytest.mark.anyio
async def test_get_by_id_returns_none_if_not_found(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    found_team = await repo.get_by_id(999)

    assert found_team is None


@pytest.mark.anyio
async def test_save_team_with_multiple_members(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(300),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MANAGER
            ),
            models.MemberTask(
                user_id=ids.UserId(2),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MEMBER
            ),
            models.MemberTask(
                user_id=ids.UserId(3),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MEMBER
            )
        ]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(300)

    assert found_team is not None
    assert found_team.id == 300
    assert len(found_team.members) == 3

    user_ids = {member.user_id for member in found_team.members}
    assert user_ids == {1, 2, 3}


@pytest.mark.anyio
async def test_save_team_with_empty_members(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(400),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(400)

    assert found_team is not None
    assert found_team.id == 400
    assert len(found_team.members) == 0


@pytest.mark.anyio
async def test_save_multiple_teams_with_different_ids(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team1 = models.Team(
        id=ids.TeamId(100),
        members=[]
    )
    team2 = models.Team(
        id=ids.TeamId(200),
        members=[]
    )

    await repo.save(team1)
    await repo.save(team2)
    await async_session.commit()

    found_team1 = await repo.get_by_id(100)
    found_team2 = await repo.get_by_id(200)

    assert found_team1 is not None
    assert found_team1.id == 100
    assert found_team2 is not None
    assert found_team2.id == 200


@pytest.mark.anyio
async def test_save_creates_new_comment(async_session):
    repo = repository.SQLAlchemyTaskCommentRepository(async_session)
    comment = models.Comment(
        id=ids.CommentId(1),
        task_id=ids.TaskId(10),
        author_id=ids.UserId(5),
        text="first comment",
        team_id=None,
    )
    await repo.save(comment)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.CommentOrm)
        .where(orm_models.CommentOrm.id == 1)
    )
    orm_comment = result.scalar_one()

    assert orm_comment.id == 1
    assert orm_comment.task_id == 10
    assert orm_comment.author_id == 5
    assert orm_comment.text == "first comment"
    assert orm_comment.team_id is None


@pytest.mark.anyio
async def test_get_by_task_id_returns_comments(async_session):
    repo = repository.SQLAlchemyTaskCommentRepository(async_session)

    comment_1 = models.Comment(
        id=ids.CommentId(1),
        task_id=ids.TaskId(10),
        author_id=ids.UserId(1),
        text="first comment",
    )
    comment_2 = models.Comment(
        id=ids.CommentId(2),
        task_id=ids.TaskId(10),
        author_id=ids.UserId(2),
        text="second comment",
    )

    comment_other_task = models.Comment(
        id=ids.CommentId(3),
        task_id=ids.TaskId(20),
        author_id=ids.UserId(3),
        text="other task comment",
    )

    await repo.save(comment_1)
    await repo.save(comment_2)
    await repo.save(comment_other_task)
    await async_session.commit()

    comments = await repo.get_by_task_id(10)

    assert len(comments) == 2
    texts = {c._text for c in comments}
    assert texts == {"first comment", "second comment"}

    for c in comments:
        assert isinstance(c, models.Comment)


@pytest.mark.anyio
async def test_save_creates_new_task(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    task = models.Task(
        id=ids.TaskId(1),
        supervisor_id=ids.UserId(10),
        team_id=ids.TeamId(30),
        executor_id=ids.UserId(20),
        deadline=datetime(2030, 1, 1, 12, 0),
        title="Test task",
        description="Task description",
    )

    await repo.save(task)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskOrm)
        .where(orm_models.TaskOrm.id == 1)
    )
    orm_task = result.scalar_one()

    assert orm_task.id == 1
    assert orm_task.supervisor_id == 10
    assert orm_task.executor_id == 20
    assert orm_task.team_id == 30
    assert orm_task.title == "Test task"
    assert orm_task.description == "Task description"


@pytest.mark.anyio
async def test_save_updates_existing_task(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    existing = orm_models.TaskOrm(
        id=1,
        supervisor_id=10,
        executor_id=20,
        team_id=30,
        deadline=datetime(2030, 1, 1, 12, 0),
        title="Old title",
        description="Old description",
    )
    async_session.add(existing)
    await async_session.commit()

    updated = models.Task(
        id=ids.TaskId(1),
        supervisor_id=ids.UserId(99),
        team_id=ids.TeamId(30),
        executor_id=ids.UserId(20),
        deadline=datetime(2031, 1, 1, 12, 0),
        title="New title",
        description="New description",
    )

    await repo.save(updated)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskOrm)
        .where(orm_models.TaskOrm.id == 1)
    )
    orm_task = result.scalar_one()

    assert orm_task.supervisor_id == 99
    assert orm_task.title == "New title"
    assert orm_task.description == "New description"


@pytest.mark.anyio
async def test_get_task_by_id(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    async_session.add(
        orm_models.TaskOrm(
            id=1,
            supervisor_id=10,
            executor_id=None,
            team_id=30,
            deadline=datetime(2030, 1, 1, 12, 0),
            title="Task",
            description="Description",
        )
    )
    await async_session.commit()

    task = await repo.get_by_id(1)

    assert task is not None
    assert task.id == 1
    assert task.supervisor_id == 10
    assert task.team_id == 30


@pytest.mark.anyio
async def test_get_task_by_id_returns_none(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)
    task = await repo.get_by_id(999)
    assert task is None


@pytest.mark.anyio
async def test_get_tasks_by_supervisor(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    async_session.add_all([
        orm_models.TaskOrm(
            id=1,
            supervisor_id=10,
            executor_id=None,
            team_id=30,
            deadline=datetime(2030, 1, 1, 12, 0),
            title="Task 1",
            description="Desc",
        ),
        orm_models.TaskOrm(
            id=2,
            supervisor_id=10,
            executor_id=None,
            team_id=31,
            deadline=datetime(2030, 1, 2, 12, 0),
            title="Task 2",
            description="Desc",
        ),
        orm_models.TaskOrm(
            id=3,
            supervisor_id=11,
            executor_id=None,
            team_id=32,
            deadline=datetime(2030, 1, 3, 12, 0),
            title="Task 3",
            description="Desc",
        ),
    ])
    await async_session.commit()

    tasks = await repo.get_by_supervisor(10)

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {1, 2}


@pytest.mark.anyio
async def test_get_tasks_by_executor(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    async_session.add_all([
        orm_models.TaskOrm(
            id=1,
            supervisor_id=10,
            executor_id=20,
            team_id=30,
            deadline=datetime(2030, 1, 1, 12, 0),
            title="Task 1",
            description="Desc",
        ),
        orm_models.TaskOrm(
            id=2,
            supervisor_id=11,
            executor_id=20,
            team_id=31,
            deadline=datetime(2030, 1, 2, 12, 0),
            title="Task 2",
            description="Desc",
        ),
        orm_models.TaskOrm(
            id=3,
            supervisor_id=12,
            executor_id=21,
            team_id=32,
            deadline=datetime(2030, 1, 3, 12, 0),
            title="Task 3",
            description="Desc",
        ),
    ])
    await async_session.commit()

    tasks = await repo.get_by_executor(20)

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {1, 2}


@pytest.mark.anyio
async def test_get_tasks_by_team(async_session):
    repo = repository.SQLAlchemyTaskRepository(async_session)

    async_session.add_all([
        orm_models.TaskOrm(
            id=1,
            supervisor_id=10,
            executor_id=None,
            team_id=30,
            deadline=datetime(2030, 1, 1, 12, 0),
            title="Task 1",
            description="Desc",
        ),
        orm_models.TaskOrm(
            id=2,
            supervisor_id=11,
            executor_id=None,
            team_id=30,
            deadline=datetime(2030, 1, 2, 12, 0),
            title="Task 2",
            description="Desc",
        ),
    ])
    await async_session.commit()

    tasks = await repo.get_by_team(30)

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {1, 2}
