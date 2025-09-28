from datetime import date
from typing import Optional, List
from pydantic import BaseModel

# ---- Meetings ----
class MeetingCreate(BaseModel):
    title: str
    date: date
    created_by: str

class MeetingOut(MeetingCreate):
    id: str
    model_config = {"from_attributes": True}

# ---- Participants ----
class ParticipantCreate(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None

class ParticipantOut(ParticipantCreate):
    id: str
    model_config = {"from_attributes": True}

# ---- Artifacts ----
class ArtifactTextIn(BaseModel):
    text: str

class ArtifactOut(BaseModel):
    id: str
    meeting_id: str
    kind: str
    url: Optional[str] = None
    model_config = {"from_attributes": True}

# ---- Summaries ----
class SummaryIn(BaseModel):
    text: str

class SummaryOut(SummaryIn):
    id: str
    meeting_id: str
    model_config = {"from_attributes": True}

# ---- Decisions ----
class DecisionIn(BaseModel):
    text: str

class DecisionOut(DecisionIn):
    id: str
    meeting_id: str
    model_config = {"from_attributes": True}

# ---- Action Items ----
class ActionItemIn(BaseModel):
    task: str                  # <-- align name with model column
    owner: Optional[str] = None
    due_date: Optional[date] = None

class ActionItemOut(ActionItemIn):
    id: str
    meeting_id: str
    model_config = {"from_attributes": True}
