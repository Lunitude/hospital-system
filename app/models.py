from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


SPECIALTIES = [
    "General Medicine",
    "Cardiology",
    "Orthopedics",
    "Neurology",
    "Pediatrics",
    "Dermatology",
    "ENT",
    "Gynecology",
    "Psychiatry",
    "Radiology",
]


class DoctorCreate(BaseModel):
    name: str
    specialty: str


class ReviewCreate(BaseModel):
    doctor_id: str
    patient_name: str
    rating: int = Field(ge=1, le=5)
    feedback: Optional[str] = None


class AdminLogin(BaseModel):
    username: str
    password: str
