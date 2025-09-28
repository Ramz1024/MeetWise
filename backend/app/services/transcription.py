import os
from google.cloud import speech
from sqlalchemy.orm import Session
from app.models import Artifact, ArtifactKind
from fastapi import HTTPException

def transcribe_audio_artifact(db: Session, artifact_id: str) -> str:
    """
    Transcribe an audio artifact using Google Cloud Speech-to-Text and save the transcript.
    Returns the transcript text.
    """
    # Fetch the artifact
    artifact = db.get(Artifact, artifact_id)
    if not artifact or artifact.kind != ArtifactKind.audio:
        raise HTTPException(status_code=400, detail="Invalid or non-audio artifact")
    
    if artifact.transcript_text:
        return artifact.transcript_text  # Return existing transcript if available

    # Initialize Google Cloud Speech client
    client = speech.SpeechClient()

    # Read audio file
    audio_path = artifact.url
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    # Configure audio settings
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # For WAV files
        sample_rate_hertz=16000,  # Adjust based on your audio
        language_code="en-US",
    )

    # Perform transcription
    try:
        response = client.recognize(config=config, audio=audio)
        transcript = " ".join(result.alternatives[0].transcript for result in response.results)
        
        # Save transcript to database
        artifact.transcript_text = transcript
        db.commit()
        db.refresh(artifact)
        return transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")