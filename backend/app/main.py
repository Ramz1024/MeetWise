# /Users/parthavikurugundla/Downloads/backend/app/main.py
from __future__ import annotations
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import engine, Base, get_db  # Revert to this
from app import models
from app.schemas import (
    MeetingCreate, MeetingOut,
    ParticipantCreate, ParticipantOut,
    ArtifactTextIn, ArtifactOut,
    SummaryIn, SummaryOut,
    DecisionIn, DecisionOut,
    ActionItemIn, ActionItemOut,
)
from app.services.transcription import transcribe_audio_artifact
from app.services.llm_processing import process_transcript_with_google_nlp, persist_nlp_outputs

app = FastAPI(title="Meetings API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(os.getcwd())
UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API running!"}

# ---- Meetings ----
@app.post("/meetings", response_model=MeetingOut, status_code=201)
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    db_meeting = models.Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@app.get("/meetings", response_model=list[MeetingOut])
def list_meetings(db: Session = Depends(get_db)):
    return db.query(models.Meeting).all()

# ---- Participants ----
@app.post("/meetings/{mid}/participants", response_model=list[ParticipantOut], status_code=201)
def add_participants(mid: str, participants: list[ParticipantCreate], db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows: list[models.Participant] = []
    for p in participants:
        row = models.Participant(meeting_id=mid, **p.dict())
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows

@app.get("/meetings/{mid}/participants", response_model=list[ParticipantOut])
def list_participants(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Participant).filter_by(meeting_id=mid).all()

# ---- Artifacts ----
@app.post("/meetings/{mid}/artifacts/text", response_model=ArtifactOut, status_code=201)
def add_text_artifact(mid: str, payload: ArtifactTextIn, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    art = models.Artifact(
        meeting_id=mid,
        kind=models.ArtifactKind.text,
        url=None,
        transcript_text=payload.text,
    )
    db.add(art); db.commit(); db.refresh(art)
    return art

@app.post("/meetings/{mid}/artifacts/audio", response_model=ArtifactOut, status_code=201)
def upload_audio_artifact(mid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    ext = os.path.splitext(file.filename or "")[1] or ".wav"
    fname = f"{mid}_{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / fname
    with path.open("wb") as f:
        f.write(file.file.read())

    art = models.Artifact(meeting_id=mid, kind=models.ArtifactKind.audio, url=str(path))
    db.add(art); db.commit(); db.refresh(art)
    return art

@app.get("/meetings/{mid}/artifacts", response_model=list[ArtifactOut])
def list_artifacts(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Artifact).filter_by(meeting_id=mid).all()

@app.patch("/artifacts/{aid}")
def patch_artifact_transcript(aid: str, data: ArtifactTextIn, db: Session = Depends(get_db)):
    art = db.get(models.Artifact, aid)
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    art.transcript_text = data.text
    db.commit(); db.refresh(art)
    return {"ok": True}

# ---- Summary / Decisions / Action Items ----
@app.post("/meetings/{mid}/summary", response_model=SummaryOut, status_code=201)
def create_summary(mid: str, payload: SummaryIn, db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    row = models.Summary(meeting_id=mid, text=payload.text)
    db.add(row); db.commit(); db.refresh(row)
    return row

@app.get("/meetings/{mid}/summary", response_model=list[SummaryOut])
def get_summaries(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Summary).filter_by(meeting_id=mid).all()

@app.post("/meetings/{mid}/decisions", response_model=list[DecisionOut], status_code=201)
def create_decisions(mid: str, items: list[DecisionIn], db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows = [models.Decision(meeting_id=mid, text=i.text) for i in items]
    db.add_all(rows); db.commit()
    for r in rows: db.refresh(r)
    return rows

@app.get("/meetings/{mid}/decisions", response_model=list[DecisionOut])
def list_decisions(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Decision).filter_by(meeting_id=mid).all()

@app.post("/meetings/{mid}/action-items", response_model=list[ActionItemOut], status_code=201)
def create_action_items(mid: str, items: list[ActionItemIn], db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows = [
        models.ActionItem(meeting_id=mid, task=i.task, owner=i.owner, due_date=i.due_date)
        for i in items
    ]
    db.add_all(rows); db.commit()
    for r in rows: db.refresh(r)
    return rows

@app.get("/meetings/{mid}/action-items", response_model=list[ActionItemOut])
def list_action_items(mid: str, db: Session = Depends(get_db)):
    return db.query(models.ActionItem).filter_by(meeting_id=mid).all()

# ---- Processing Endpoint ----
@app.post("/meetings/{id}/process", status_code=202)
async def process_meeting(id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Start an asynchronous job to process meeting artifacts, generate summaries, decisions, and action items.
    """
    # Verify meeting exists
    meeting = db.get(models.Meeting, id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Add background task
    background_tasks.add_task(process_meeting_artifacts, id, db)
    return {"message": "Processing started", "meeting_id": id}

async def process_meeting_artifacts(meeting_id: str, db: Session):
    """
    Background task to process meeting artifacts.
    """
    # Fetch all artifacts for the meeting
    artifacts = db.query(models.Artifact).filter_by(meeting_id=meeting_id).all()
    combined_transcript = []

    # Process each artifact
    for artifact in artifacts:
        if artifact.kind == models.ArtifactKind.audio and not artifact.transcript_text:
            # Transcribe audio artifact
            transcript = transcribe_audio_artifact(db, artifact.id)
            combined_transcript.append(transcript)
        elif artifact.kind == models.ArtifactKind.text or (artifact.kind == models.ArtifactKind.audio and artifact.transcript_text):
            combined_transcript.append(artifact.transcript_text or "")

    # Combine all transcripts
    combined_text = "\n".join(combined_transcript)

    # Process with LLM
    llm_output = process_transcript_with_llm(combined_text)

    # Persist outputs
    persist_llm_outputs(meeting_id, llm_output, db)