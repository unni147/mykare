from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, List

class AppointmentBase(BaseModel):
    name: str
    phone_number: str
    appointment_date: date
    appointment_time: time

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[str] = None

class Appointment(AppointmentBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
