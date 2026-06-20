from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.appointment import ConversationSummary
from app.services.stt_service import transcribe_audio
from app.services.llm_service import process_chat, generate_summary
from app.services.tts_service import generate_speech
from pydantic import BaseModel

router = APIRouter()

class ConversationResponse(BaseModel):
    transcript: str
    reply: str
    audio_base64: str
    tools: list[str]
    
@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(
    session_id: str = Form(...),
    audio: UploadFile = File(...)
):
    # 1. STT
    transcript = await transcribe_audio(audio)
    
    # 2. LLM + Function Calling
    chat_result = process_chat(session_id, transcript)
    reply_text = chat_result["reply"]
    tools = chat_result["tools"]
    
    # 3. TTS
    audio_b64 = await generate_speech(reply_text)
    
    return ConversationResponse(
        transcript=transcript,
        reply=reply_text,
        audio_base64=audio_b64,
        tools=tools
    )

@router.post("/conversation/{session_id}/summary")
def get_summary(session_id: str, db: Session = Depends(get_db)):
    data = generate_summary(session_id)
    if "error" not in data:
        # Check if already saved
        existing = db.query(ConversationSummary).filter(ConversationSummary.session_id == session_id).first()
        if existing:
            return data
            
        db_summary = ConversationSummary(
            session_id=session_id,
            name=data.get("name"),
            phone_number=data.get("phone_number"),
            intent=data.get("intent"),
            appointment_date=data.get("appointment_date"),
            appointment_time=data.get("appointment_time"),
            actions=str(data.get("actions")) if data.get("actions") else None
        )
        db.add(db_summary)
        db.commit()
    return data
