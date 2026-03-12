from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from datetime import datetime
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/review/{doctor_id}", response_class=HTMLResponse)
async def review_form(request: Request, doctor_id: str):
    db = get_db()
    try:
        doc = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc["id"] = str(doc["_id"])
    return templates.TemplateResponse("review.html", {"request": request, "doctor": doc})


@router.post("/review/{doctor_id}", response_class=HTMLResponse)
async def submit_review(
    request: Request,
    doctor_id: str,
    patient_name: str = Form(...),
    rating: int = Form(...),
    feedback: str = Form(""),
):
    db = get_db()
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    try:
        doc = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    review = {
        "doctor_id": doctor_id,
        "patient_name": patient_name.strip(),
        "rating": rating,
        "feedback": feedback.strip(),
        "created_at": datetime.utcnow(),
    }
    await db.reviews.insert_one(review)
    return RedirectResponse(url=f"/doctor/{doctor_id}?reviewed=1", status_code=303)
