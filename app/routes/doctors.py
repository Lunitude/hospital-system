from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from app.database import get_db
from app.models import SPECIALTIES

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def doctor_helper(doc):
    doc["id"] = str(doc["_id"])
    return doc


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, specialty: str = ""):
    db = get_db()
    query = {}
    if specialty:
        query["specialty"] = specialty

    cursor = db.doctors.find(query)
    doctors = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        # Calculate average rating
        pipeline = [
            {"$match": {"doctor_id": str(doc["_id"])}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        stats = await db.reviews.aggregate(pipeline).to_list(1)
        doc["avg_rating"] = round(stats[0]["avg"], 1) if stats else 0
        doc["total_reviews"] = stats[0]["count"] if stats else 0
        doctors.append(doc)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "doctors": doctors,
        "specialties": SPECIALTIES,
        "selected_specialty": specialty,
    })


@router.get("/doctor/{doctor_id}", response_class=HTMLResponse)
async def doctor_profile(request: Request, doctor_id: str):
    db = get_db()
    try:
        doc = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc["id"] = str(doc["_id"])

    # Reviews
    reviews = []
    async for r in db.reviews.find({"doctor_id": doctor_id}).sort("created_at", -1):
        r["id"] = str(r["_id"])
        reviews.append(r)

    # Stats
    pipeline = [
        {"$match": {"doctor_id": doctor_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    stats = await db.reviews.aggregate(pipeline).to_list(1)
    doc["avg_rating"] = round(stats[0]["avg"], 1) if stats else 0
    doc["total_reviews"] = stats[0]["count"] if stats else 0

    # Rating breakdown
    breakdown = {}
    for i in range(1, 6):
        count = await db.reviews.count_documents({"doctor_id": doctor_id, "rating": i})
        breakdown[i] = count

    return templates.TemplateResponse("doctor.html", {
        "request": request,
        "doctor": doc,
        "reviews": reviews,
        "breakdown": breakdown,
    })
