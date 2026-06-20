from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.appointment import Appointment
from app.api.schemas import AppointmentCreate, AppointmentUpdate, Appointment as AppointmentSchema

router = APIRouter()

@router.post("/appointments", response_model=AppointmentSchema)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check for double booking
    existing_appointment = db.query(Appointment).filter(
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.appointment_time == appointment.appointment_time,
        Appointment.status != "Cancelled"
    ).first()
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Slot already booked.")
        
    db_appointment = Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/appointments", response_model=List[AppointmentSchema])
def read_appointments(phone_number: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Appointment)
    if phone_number:
        query = query.filter(Appointment.phone_number == phone_number)
    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.put("/appointments/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(appointment_id: int, appointment: AppointmentUpdate, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = appointment.model_dump(exclude_unset=True)
    
    # Check for double booking if date/time is changing
    if "appointment_date" in update_data or "appointment_time" in update_data:
        new_date = update_data.get("appointment_date", db_appointment.appointment_date)
        new_time = update_data.get("appointment_time", db_appointment.appointment_time)
        existing_appointment = db.query(Appointment).filter(
            Appointment.appointment_date == new_date,
            Appointment.appointment_time == new_time,
            Appointment.id != appointment_id,
            Appointment.status != "Cancelled"
        ).first()
        if existing_appointment:
            raise HTTPException(status_code=400, detail="Slot already booked.")
            
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
        
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_appointment.status = "Cancelled"
    db.commit()
    return {"message": "Appointment cancelled successfully"}
