from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime, date
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

@dataclass
class Workspace:
    name: str
    domain: str
    id: str = field(default_factory=generate_uuid)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class User:
    email: str
    name: str
    workspace_id: str
    department: str
    role: str = "Member"
    avatar_url: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class Team:
    name: str
    workspace_id: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class TeamMembership:
    user_id: str
    team_id: str
    role: str = "Member"

@dataclass
class Project:
    name: str
    workspace_id: str
    team_id: Optional[str] = None
    owner_id: Optional[str] = None
    description: Optional[str] = None
    archived: bool = False
    color: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class Section:
    name: str
    project_id: str
    order_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class Task:
    name: str
    workspace_id: str
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    assignee_id: Optional[str] = None
    parent_id: Optional[str] = None 
    description: Optional[str] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    priority: str = "Medium"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class Story:
    target_id: str # Task ID usually
    text: str
    created_by: str
    target_type: str = "task"
    type: str = "comment"
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_uuid)

@dataclass
class CustomFieldDefinition:
    name: str
    type: str # text, number, enum
    workspace_id: str
    description: Optional[str] = None
    enum_options: Optional[Dict[str, Any]] = None
    id: str = field(default_factory=generate_uuid)

@dataclass
class CustomFieldValue:
    task_id: str
    field_id: str
    value: Optional[str] = None
    value_number: Optional[float] = None
