from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Team, Message
from app.dependencies import get_current_user

router = APIRouter(tags=["chat"])


def _msg_out(m: Message) -> dict:
    return {
        "id": m.id,
        "team_id": m.team_id,
        "user_id": m.user_id,
        "user_email": m.user.email if m.user else None,
        "content": m.content,
        "created_at": m.created_at,
    }


def _require_member(team_id: int, user: User, db: Session) -> Team:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail={"code": "TEAM_NOT_FOUND"})
    if user.team_id != team_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return team


class SendMessageRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content cannot be empty")
        if len(v) > 1000:
            raise ValueError("content exceeds 1000 characters")
        return v


@router.post("/teams/{team_id}/messages", status_code=201)
def send_message(
    team_id: int,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_member(team_id, current_user, db)
    msg = Message(team_id=team_id, user_id=current_user.id, content=body.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _msg_out(msg)


@router.get("/teams/{team_id}/messages")
def list_messages(
    team_id: int,
    since: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_member(team_id, current_user, db)
    q = db.query(Message).filter(Message.team_id == team_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            q = q.filter(Message.created_at > since_dt)
        except ValueError:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SINCE"})
        return [_msg_out(m) for m in q.order_by(Message.created_at.asc()).all()]
    # 초기 로드: 최근 50개 (오래된 순 반환)
    messages = q.order_by(Message.created_at.desc()).limit(50).all()
    return [_msg_out(m) for m in reversed(messages)]


@router.delete("/messages/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail={"code": "MESSAGE_NOT_FOUND"})
    if msg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    db.delete(msg)
    db.commit()
    return {"message": "삭제되었습니다"}
