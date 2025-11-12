# backend/models/appointment.py
"""Appointment, WeeklyCoverage, and PractitionerDailySchedule models"""

from typing import Optional, List
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class AppointmentStatus(str, Enum):
    """Appointment status options"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, Enum):
    """Appointment type options"""
    REGULAR = "regular"
    WALK_IN = "walk_in"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"
    CHECKUP = "checkup"
    IMMUNIZATION = "immunization"
    PRENATAL = "prenatal"
    POSTNATAL = "postnatal"


class Appointment(MongoBaseModel):
    """Appointment collection model"""
    appointment_id: str = Field(..., description="Unique appointment identifier")
    patient_id: str = Field(..., description="Reference to Patient")
    staff_id: str = Field(..., description="Reference to Staff (practitioner)")
    
    # Scheduling information
    scheduled_date: date = Field(..., description="Date of appointment")
    scheduled_start: time = Field(..., description="Scheduled start time")
    scheduled_end: time = Field(..., description="Scheduled end time")
    actual_start: Optional[datetime] = Field(None, description="Actual start time")
    actual_end: Optional[datetime] = Field(None, description="Actual end time")
    
    # Appointment details
    appointment_type: AppointmentType = Field(default=AppointmentType.REGULAR)
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    reason_for_visit: str = Field(..., max_length=500, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # Walk-in specific
    is_walk_in: bool = Field(default=False, description="Whether this is a walk-in appointment")
    walk_in_arrival_time: Optional[datetime] = Field(None, description="When walk-in patient arrived")
    
    # Confirmation and reminders
    confirmation_sent: bool = Field(default=False)
    confirmation_sent_at: Optional[datetime] = None
    reminder_sent: bool = Field(default=False)
    reminder_sent_at: Optional[datetime] = None
    
    # Cancellation/Rescheduling
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[str] = Field(None, description="Staff ID who cancelled")
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[str] = Field(None, description="Previous appointment ID if rescheduled")
    
    @validator('scheduled_end')
    def validate_end_after_start(cls, v, values):
        if 'scheduled_start' in values and v <= values['scheduled_start']:
            raise ValueError('Scheduled end time must be after start time')
        return v
    
    @validator('scheduled_start')
    def validate_appointment_slot(cls, v):
        # Ensure appointment starts at 10-minute intervals
        if v.minute % 10 != 0:
            raise ValueError('Appointments must start at 10-minute intervals')
        return v
    
    @property
    def duration_minutes(self) -> int:
        """Calculate scheduled duration in minutes"""
        if self.scheduled_start and self.scheduled_end:
            start_dt = datetime.combine(date.today(), self.scheduled_start)
            end_dt = datetime.combine(date.today(), self.scheduled_end)
            return int((end_dt - start_dt).total_seconds() / 60)
        return 10  # Default appointment duration
    
    class Config:
        schema_extra = {
            "example": {
                "appointment_id": "APT001",
                "patient_id": "PAT001",
                "staff_id": "STF001",
                "scheduled_date": "2024-02-01",
                "scheduled_start": "09:00:00",
                "scheduled_end": "09:10:00",
                "appointment_type": "regular",
                "status": "scheduled",
                "reason_for_visit": "Annual checkup",
                "is_walk_in": False
            }
        }


class WeeklyCoverage(MongoBaseModel):
    """WeeklyCoverage collection model"""
    coverage_id: str = Field(..., description="Unique coverage identifier")
    week_start: date = Field(..., description="Monday of the coverage week")
    week_end: date = Field(..., description="Sunday of the coverage week")
    
    # Staff assignments
    staff_assignments: List[dict] = Field(..., description="Staff assignments for the week")
    # Format: [{"staff_id": "STF001", "role": "physician", "days": ["monday", "tuesday"]}]
    
    # On-call information
    on_call_assignments: List[dict] = Field(..., description="On-call assignments")
    # Format: [{"staff_id": "STF001", "date": "2024-02-01", "phone": "+14165551234"}]
    
    # Coverage requirements
    min_physicians: int = Field(default=2, description="Minimum physicians per shift")
    min_nurses: int = Field(default=1, description="Minimum nurses per shift")
    min_midwives: int = Field(default=1, description="Minimum midwives per shift")
    
    notes: Optional[str] = Field(None, description="Coverage notes")
    created_by: str = Field(..., description="Staff ID who created schedule")
    approved: bool = Field(default=False, description="Whether schedule is approved")
    approved_by: Optional[str] = Field(None, description="Staff ID who approved")
    approved_at: Optional[datetime] = None
    
    @validator('week_start')
    def validate_week_start_is_monday(cls, v):
        if v.weekday() != 0:  # 0 is Monday
            raise ValueError('Week start must be a Monday')
        return v
    
    @validator('week_end')
    def validate_week_end(cls, v, values):
        if 'week_start' in values:
            expected_end = values['week_start'] + timedelta(days=6)
            if v != expected_end:
                raise ValueError('Week end must be Sunday of the same week')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "coverage_id": "COV001",
                "week_start": "2024-01-29",
                "week_end": "2024-02-04",
                "staff_assignments": [
                    {"staff_id": "STF001", "role": "physician", "days": ["monday", "tuesday", "wednesday"]},
                    {"staff_id": "STF002", "role": "nurse", "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]}
                ],
                "on_call_assignments": [
                    {"staff_id": "STF001", "date": "2024-01-29", "phone": "+14165551234"}
                ],
                "created_by": "STF000"
            }
        }


class PractitionerDailySchedule(MongoBaseModel):
    """PractitionerDailySchedule collection model"""
    schedule_id: str = Field(..., description="Unique schedule identifier")
    staff_id: str = Field(..., description="Reference to Staff")
    schedule_date: date = Field(..., description="Date of the schedule")
    
    # Working hours
    start_time: time = Field(..., description="Start time of practitioner's day")
    end_time: time = Field(..., description="End time of practitioner's day")
    
    # Break times
    break_slots: List[dict] = Field(default_factory=list, description="Break time slots")
    # Format: [{"start": "12:00:00", "end": "13:00:00", "type": "lunch"}]
    
    # Availability
    is_available: bool = Field(default=True, description="Whether practitioner is available")
    available_for_walk_ins: bool = Field(default=True, description="Whether accepting walk-ins")
    
    # Appointment slots
    total_slots: int = Field(..., description="Total appointment slots for the day")
    booked_slots: int = Field(default=0, description="Number of booked slots")
    blocked_slots: List[dict] = Field(default_factory=list, description="Blocked time slots")
    # Format: [{"start": "14:00:00", "end": "14:30:00", "reason": "meeting"}]
    
    # Walk-in hours
    walk_in_start: Optional[time] = Field(None, description="Start of walk-in hours")
    walk_in_end: Optional[time] = Field(None, description="End of walk-in hours")
    max_walk_ins: Optional[int] = Field(None, description="Maximum walk-ins for the day")
    current_walk_ins: int = Field(default=0, description="Current number of walk-ins")
    
    notes: Optional[str] = Field(None, description="Schedule notes")
    
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('total_slots')
    def calculate_total_slots(cls, v, values):
        if 'start_time' in values and 'end_time' in values:
            start_dt = datetime.combine(date.today(), values['start_time'])
            end_dt = datetime.combine(date.today(), values['end_time'])
            duration_minutes = (end_dt - start_dt).total_seconds() / 60
            
            # Subtract break time
            break_minutes = 0
            if 'break_slots' in values:
                for break_slot in values.get('break_slots', []):
                    break_start = datetime.combine(date.today(), time.fromisoformat(break_slot['start']))
                    break_end = datetime.combine(date.today(), time.fromisoformat(break_slot['end']))
                    break_minutes += (break_end - break_start).total_seconds() / 60
            
            # Calculate slots (10 minutes each)
            available_minutes = duration_minutes - break_minutes
            return int(available_minutes / 10)
        return v
    
    @property
    def available_slots(self) -> int:
        """Calculate available appointment slots"""
        return self.total_slots - self.booked_slots - len(self.blocked_slots)
    
    @property
    def utilization_rate(self) -> float:
        """Calculate schedule utilization percentage"""
        if self.total_slots > 0:
            return (self.booked_slots / self.total_slots) * 100
        return 0.0
    
    class Config:
        schema_extra = {
            "example": {
                "schedule_id": "SCH001",
                "staff_id": "STF001",
                "schedule_date": "2024-02-01",
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "break_slots": [
                    {"start": "12:00:00", "end": "13:00:00", "type": "lunch"}
                ],
                "is_available": True,
                "available_for_walk_ins": True,
                "total_slots": 42,
                "booked_slots": 20,
                "walk_in_start": "14:00:00",
                "walk_in_end": "16:00:00"
            }
        }


# Request models for API
class AppointmentCreateRequest(BaseModel):
    """Request model for creating an appointment"""
    patient_id: str
    staff_id: str
    scheduled_date: date
    scheduled_start: time
    scheduled_end: Optional[time] = None  # If not provided, default to 10 minutes
    appointment_type: AppointmentType = AppointmentType.REGULAR
    reason_for_visit: str
    notes: Optional[str] = None


class AppointmentUpdateRequest(BaseModel):
    """Request model for updating an appointment"""
    scheduled_date: Optional[date] = None
    scheduled_start: Optional[time] = None
    scheduled_end: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    reason_for_visit: Optional[str] = None
    notes: Optional[str] = None


class WalkInRequest(BaseModel):
    """Request model for walk-in registration"""
    patient_id: str
    reason_for_visit: str
    preferred_staff_id: Optional[str] = None
    notes: Optional[str] = None


class ScheduleFilterRequest(BaseModel):
    """Request model for filtering schedules"""
    date: date
    staff_id: Optional[str] = None
    include_availability: bool = True
    include_appointments: bool = False