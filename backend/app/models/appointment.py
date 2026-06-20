from sqlalchemy import Column, Integer, String, Date, Time, DateTime
from datetime import datetime
from app.db.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, index=True)
    appointment_date = Column(Date, index=True)
    appointment_time = Column(Time)
    status = Column(String, default="Booked")
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    appointment_date = Column(String, nullable=True)
    appointment_time = Column(String, nullable=True)
    actions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
