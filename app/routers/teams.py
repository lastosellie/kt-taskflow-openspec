import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Team
from app.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])


def _gen_invite_code() -> str:
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(letters, k=4)) + "-" + "".join(random.choices(letters, k=4))


def _require_member(team: Team, user: User):
    if user.team_id != team.id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


class CreateTeamRequest(BaseModel):
    name: str


class JoinRequest(BaseModel):
    invite_code: str


@router.post("", status_code=201)
def create_team(
    body: CreateTeamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id is not None:
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_IN_TEAM", "message": "이미 다른 팀에 소속되어 있습니다. 먼저 팀을 떠나세요."},
        )
    # invite_code 충돌 방지 루프
    for _ in range(10):
        code = _gen_invite_code()
        if not db.query(Team).filter(Team.invite_code == code).first():
            break

    team = Team(name=body.name, invite_code=code, owner_id=current_user.id)
    db.add(team)
    db.flush()  # team.id 확보

    current_user.team_id = team.id
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}


@router.get("/{team_id}")
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail={"code": "TEAM_NOT_FOUND"})
    _require_member(team, current_user)
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}


@router.post("/join")
def join_team(
    body: JoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(Team.invite_code == body.invite_code).first()
    if not team:
        raise HTTPException(
            status_code=404,
            detail={"code": "TEAM_NOT_FOUND", "message": "유효하지 않은 초대코드입니다"},
        )
    if current_user.team_id == team.id:
        return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}
    if current_user.team_id is not None:
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_IN_TEAM", "message": "이미 다른 팀에 소속되어 있습니다. 먼저 팀을 떠나세요."},
        )
    current_user.team_id = team.id
    db.commit()
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}


@router.get("/{team_id}/members")
def list_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail={"code": "TEAM_NOT_FOUND"})
    _require_member(team, current_user)
    members = db.query(User).filter(User.team_id == team_id).all()
    return [{"id": m.id, "email": m.email, "created_at": m.created_at} for m in members]


@router.delete("/{team_id}/leave")
def leave_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail={"code": "TEAM_NOT_FOUND"})
    _require_member(team, current_user)
    if team.owner_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": "OWNER_CANNOT_LEAVE", "message": "팀 owner는 팀을 떠날 수 없습니다"},
        )
    current_user.team_id = None
    db.commit()
    return {"message": "팀을 떠났습니다"}
