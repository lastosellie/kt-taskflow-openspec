import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", use_alter=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    owned_teams = relationship("Team", foreign_keys="Team.owner_id", back_populates="owner")
    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    messages = relationship("Message", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_teams")
    members = relationship("User", foreign_keys="User.team_id", back_populates="team")
    tasks = relationship("Task", back_populates="team")
    messages = relationship("Message", back_populates="team")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="tasks")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="messages")
    user = relationship("User", back_populates="messages")
