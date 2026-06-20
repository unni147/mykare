from app.db.database import SessionLocal
from app.models.appointment import Appointment
from datetime import datetime, date, time

def identify_user(phone_number: str) -> str:
    """Identify if a user has any existing appointments using their phone number."""
    db = SessionLocal()
    try:
        user = db.query(Appointment).filter(Appointment.phone_number == phone_number).first()
        if user:
            return f"User identified: {user.name}"
        return "No existing user found with this phone number."
    finally:
        db.close()

def fetch_slots(target_date: str) -> str:
    """Fetch available appointment slots for a given date. You must format the target_date as YYYY-MM-DD internally."""
    db = SessionLocal()
    try:
        try:
            d = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD."
        
        all_slots = [time(hour=h) for h in range(9, 17)]
        
        existing = db.query(Appointment).filter(
            Appointment.appointment_date == d,
            Appointment.status != "Cancelled"
        ).all()
        booked_times = [appt.appointment_time for appt in existing]
        
        available = [t.strftime("%H:%M") for t in all_slots if t not in booked_times]
        
        if not available:
            return f"No slots available on {target_date}."
        return f"Available slots on {target_date}: {', '.join(available)}"
    finally:
        db.close()

def book_appointment(name: str, phone_number: str, appointment_date: str, appointment_time: str) -> str:
    """Book a new appointment. You must format the date as YYYY-MM-DD and time as HH:MM internally."""
    db = SessionLocal()
    try:
        try:
            d = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            t = datetime.strptime(appointment_time, "%H:%M").time()
        except ValueError:
            return "Invalid date/time format. Use YYYY-MM-DD and HH:MM."
            
        existing = db.query(Appointment).filter(
            Appointment.appointment_date == d,
            Appointment.appointment_time == t,
            Appointment.status != "Cancelled"
        ).first()
        
        if existing:
            return "Error: Slot already booked. Please choose another time."
            
        new_appt = Appointment(
            name=name,
            phone_number=phone_number,
            appointment_date=d,
            appointment_time=t,
            status="Booked"
        )
        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)
        return f"SUCCESS: Appointment booked successfully. ID: {new_appt.id}, Date: {appointment_date}, Time: {appointment_time}."
    finally:
        db.close()

def retrieve_appointments(phone_number: str) -> str:
    """Retrieve all appointments for a given phone number."""
    db = SessionLocal()
    try:
        appts = db.query(Appointment).filter(Appointment.phone_number == phone_number).all()
        if not appts:
            return "No appointments found for this phone number."
            
        result = []
        for appt in appts:
            result.append(f"ID: {appt.id}, Date: {appt.appointment_date}, Time: {appt.appointment_time}, Status: {appt.status}")
        return "\n".join(result)
    finally:
        db.close()

def cancel_appointment(appointment_id: int) -> str:
    """Cancel an appointment by its ID."""
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return "Error: Appointment not found."
            
        appt.status = "Cancelled"
        db.commit()
        return f"Appointment {appointment_id} has been cancelled."
    finally:
        db.close()

def modify_appointment(appointment_id: int, new_date: str, new_time: str) -> str:
    """Modify the date and time of an existing appointment. You must format the date as YYYY-MM-DD and time as HH:MM internally."""
    db = SessionLocal()
    try:
        try:
            d = datetime.strptime(new_date, "%Y-%m-%d").date()
            t = datetime.strptime(new_time, "%H:%M").time()
        except ValueError:
            return "Invalid date/time format. Use YYYY-MM-DD and HH:MM."
            
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return "Error: Appointment not found."
            
        existing = db.query(Appointment).filter(
            Appointment.appointment_date == d,
            Appointment.appointment_time == t,
            Appointment.id != appointment_id,
            Appointment.status != "Cancelled"
        ).first()
        
        if existing:
            return "Error: The new slot is already booked. Please choose another time."
            
        appt.appointment_date = d
        appt.appointment_time = t
        appt.status = "Booked"
        db.commit()
        return f"Appointment {appointment_id} successfully updated to {new_date} at {new_time}."
    finally:
        db.close()

def end_conversation() -> str:
    """End the conversation and trigger summary generation."""
    return "Conversation ended. Goodbye!"

tools_list = [
    identify_user,
    fetch_slots,
    book_appointment,
    retrieve_appointments,
    cancel_appointment,
    modify_appointment,
    end_conversation
]
