from google.cloud import language_v1
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Summary, Decision, ActionItem
import re

class NLPOutput(BaseModel):
    summary: str
    decisions: List[str]
    action_items: List[dict]  # Each dict has task, owner, due_date

def process_transcript_with_google_nlp(transcript: str) -> NLPOutput:
    """
    Process the transcript using Google Cloud Natural Language API to generate summary, decisions, and action items.
    """
    client = language_v1.LanguageServiceClient()

    # Prepare document for NLP
    document = language_v1.Document(content=transcript, type_=language_v1.Document.Type.PLAIN_TEXT)

    # Analyze entities and syntax
    entity_response = client.analyze_entities(document=document)
    syntax_response = client.analyze_syntax(document=document)

    # Generate summary (simple truncation for brevity)
    summary = transcript[:200] + "..." if len(transcript) > 200 else transcript

    # Extract decisions (sentences with verbs like "decided", "agreed")
    decisions = []
    decision_keywords = ["decided", "agreed", "chosen", "selected"]
    sentences = [s.text.content for s in syntax_response.sentences]
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in decision_keywords):
            decisions.append(sentence.strip())

    # Extract action items (sentences with verbs like "will", "to", and entities like PERSON, DATE)
    action_items = []
    for sentence in sentences:
        if "will" in sentence.lower() or "to" in sentence.lower():
            task = sentence.strip()
            owner = None
            due_date = None

            # Find PERSON entities for owner
            for entity in entity_response.entities:
                if entity.type_ == language_v1.Entity.Type.PERSON and entity.name in sentence:
                    owner = entity.name

            # Find DATE entities for due_date
            for entity in entity_response.entities:
                if entity.type_ == language_v1.Entity.Type.DATE:
                    # Attempt to parse date (basic handling)
                    try:
                        # Look for ISO-like dates or relative dates like "next week"
                        if re.match(r"\d{4}-\d{2}-\d{2}", entity.name):
                            due_date = date.fromisoformat(entity.name)
                        elif "next week" in entity.name.lower():
                            due_date = (datetime.now() + timedelta(days=7)).date()
                    except ValueError:
                        continue

            if task:
                action_items.append({"task": task, "owner": owner, "due_date": due_date.isoformat() if due_date else None})

    return NLPOutput(
        summary=summary,
        decisions=decisions,
        action_items=action_items
    )

def persist_nlp_outputs(meeting_id: str, nlp_output: NLPOutput, db: Session):
    """
    Persist NLP outputs to the Summaries, Decisions, and ActionItems tables.
    """
    # Save summary
    summary = Summary(meeting_id=meeting_id, text=nlp_output.summary)
    db.add(summary)

    # Save decisions
    decisions = [Decision(meeting_id=meeting_id, text=text) for text in nlp_output.decisions]
    db.add_all(decisions)

    # Save action items
    action_items = [
        ActionItem(
            meeting_id=meeting_id,
            task=item["task"],
            owner=item.get("owner"),
            due_date=date.fromisoformat(item["due_date"]) if item.get("due_date") else None
        )
        for item in nlp_output.action_items
    ]
    db.add_all(action_items)

    db.commit()