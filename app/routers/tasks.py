from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Team, Task, TaskStatus
from app.dependencies import get_current_user

router = APIRouter(tags=["tasks"])


def _task_out(t: Task) -> dict:
    return {
        "id": t.id,
        "team_id": t.team_id,
        "title": t.title,
        "status": t.status,
        "creator_id": t.creator_id,
        "assignee_id": t.assignee_id,
        "created_at": t.created_at,
    }


def _require_team_member(team_id: int, user: User, db: Session) -> Team:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail={"code": "TEAM_NOT_FOUND"})
    if user.team_id != team_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return team


# ── 태스크 생성 ──────────────────────────────────────────────────────────────

class CreateTaskRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


@router.post("/teams/{team_id}/tasks", status_code=201)
def create_task(
    team_id: int,
    body: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_member(team_id, current_user, db)
    task = Task(
        team_id=team_id,
        title=body.title,
        status=TaskStatus.TODO,
        creator_id=current_user.id,
        assignee_id=body.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_out(task)


# ── 태스크 목록 조회 ──────────────────────────────────────────────────────────

@router.get("/teams/{team_id}/tasks")
def list_tasks(
    team_id: int,
    filter: Optional[str] = Query(None, pattern="^(@me|unassigned)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_member(team_id, current_user, db)
    q = db.query(Task).filter(Task.team_id == team_id)
    if filter == "@me":
        q = q.filter(Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        q = q.filter(Task.assignee_id == None)  # noqa: E711
    return [_task_out(t) for t in q.all()]


# ── 태스크 단건 조회 ──────────────────────────────────────────────────────────

@router.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND"})
    _require_team_member(task.team_id, current_user, db)
    return _task_out(task)


# ── 상태 변경 (드래그 앤 드롭) ───────────────────────────────────────────────

class StatusPatch(BaseModel):
    status: TaskStatus


@router.patch("/tasks/{task_id}/status")
def patch_task_status(
    task_id: int,
    body: StatusPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND"})
    _require_team_member(task.team_id, current_user, db)
    task.status = body.status
    db.commit()
    db.refresh(task)
    return _task_out(task)


# ── 상세 수정 (카드 모달) ─────────────────────────────────────────────────────

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[int] = None


@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    body: UpdateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND"})
    team = _require_team_member(task.team_id, current_user, db)
    if body.title is not None:
        task.title = body.title
    if "assignee_id" in body.model_fields_set:
        task.assignee_id = body.assignee_id
    db.commit()
    db.refresh(task)
    return _task_out(task)


# ── 태스크 삭제 ───────────────────────────────────────────────────────────────

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND"})
    team = _require_team_member(task.team_id, current_user, db)
    is_owner = team.owner_id == current_user.id
    if not is_owner and task.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "본인이 생성한 태스크만 삭제할 수 있습니다"},
        )
    db.delete(task)
    db.commit()
    return {"message": "삭제되었습니다"}
