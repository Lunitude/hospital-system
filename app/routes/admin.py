from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
import aiofiles
import os
import uuid

from app.database import get_db
from app.models import SPECIALTIES

router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "hospital_secret_key_2024_secure"
ALGORITHM = "HS256"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def create_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_current_admin(admin_token: str = None):
    if not admin_token:
        return None
    return verify_token(admin_token)


# ── Login ──────────────────────────────────────────────────────────────────

@router.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get("admin_token")
    if token and verify_token(token):
        return RedirectResponse(url="/admin/dashboard")
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@router.post("/admin/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_db()
    admin = await db.admins.find_one({"username": username})
    if not admin or not pwd_context.verify(password, admin["password"]):
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    token = create_token(username)
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie("admin_token", token, httponly=True, max_age=28800)
    return response


@router.get("/admin/logout")
async def logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_token")
    return response


# ── Dashboard ──────────────────────────────────────────────────────────────

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")

    db = get_db()
    total_doctors = await db.doctors.count_documents({})
    total_reviews = await db.reviews.count_documents({})

    # Recent reviews with doctor info
    recent_reviews = []
    async for r in db.reviews.find().sort("created_at", -1).limit(5):
        r["id"] = str(r["_id"])
        try:
            doc = await db.doctors.find_one({"_id": ObjectId(r["doctor_id"])})
            r["doctor_name"] = doc["name"] if doc else "Unknown"
        except Exception:
            r["doctor_name"] = "Unknown"
        recent_reviews.append(r)

    doctors = []
    async for d in db.doctors.find().sort("name", 1):
        d["id"] = str(d["_id"])
        doctors.append(d)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_doctors": total_doctors,
        "total_reviews": total_reviews,
        "recent_reviews": recent_reviews,
        "doctors": doctors,
    })


# ── Add Doctor ─────────────────────────────────────────────────────────────

@router.get("/admin/add-doctor", response_class=HTMLResponse)
async def add_doctor_page(request: Request):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin_add_doctor.html", {
        "request": request,
        "specialties": SPECIALTIES,
        "success": None,
        "error": None,
    })


@router.post("/admin/add-doctor", response_class=HTMLResponse)
async def add_doctor(
    request: Request,
    name: str = Form(...),
    specialty: str = Form(...),
    image: UploadFile = File(None),
):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")

    db = get_db()
    image_path = None

    if image and image.filename:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            return templates.TemplateResponse("admin_add_doctor.html", {
                "request": request,
                "specialties": SPECIALTIES,
                "error": "Only JPG, PNG, WEBP images allowed",
                "success": None,
            })
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(filepath, "wb") as f:
            content = await image.read()
            await f.write(content)
        image_path = f"/static/uploads/{filename}"

    doctor = {
        "name": name.strip(),
        "specialty": specialty,
        "image": image_path,
        "created_at": datetime.utcnow(),
    }
    await db.doctors.insert_one(doctor)

    return templates.TemplateResponse("admin_add_doctor.html", {
        "request": request,
        "specialties": SPECIALTIES,
        "success": f"Dr. {name} added successfully!",
        "error": None,
    })


# ── Delete Doctor ──────────────────────────────────────────────────────────

@router.post("/admin/delete-doctor/{doctor_id}")
async def delete_doctor(request: Request, doctor_id: str):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")
    db = get_db()
    try:
        await db.doctors.delete_one({"_id": ObjectId(doctor_id)})
        await db.reviews.delete_many({"doctor_id": doctor_id})
    except Exception:
        pass
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ── Manage Reviews ─────────────────────────────────────────────────────────

@router.get("/admin/manage-reviews", response_class=HTMLResponse)
async def manage_reviews(request: Request, doctor_id: str = ""):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")

    db = get_db()
    query = {}
    if doctor_id:
        query["doctor_id"] = doctor_id

    reviews = []
    async for r in db.reviews.find(query).sort("created_at", -1):
        r["id"] = str(r["_id"])
        try:
            doc = await db.doctors.find_one({"_id": ObjectId(r["doctor_id"])})
            r["doctor_name"] = doc["name"] if doc else "Unknown"
            r["doctor_specialty"] = doc["specialty"] if doc else ""
        except Exception:
            r["doctor_name"] = "Unknown"
            r["doctor_specialty"] = ""
        reviews.append(r)

    doctors = []
    async for d in db.doctors.find().sort("name", 1):
        d["id"] = str(d["_id"])
        doctors.append(d)

    return templates.TemplateResponse("admin_manage_reviews.html", {
        "request": request,
        "reviews": reviews,
        "doctors": doctors,
        "selected_doctor": doctor_id,
    })


@router.post("/admin/delete-review/{review_id}")
async def delete_review(request: Request, review_id: str):
    token = request.cookies.get("admin_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/admin/login")
    db = get_db()
    try:
        await db.reviews.delete_one({"_id": ObjectId(review_id)})
    except Exception:
        pass
    referer = request.headers.get("referer", "/admin/manage-reviews")
    return RedirectResponse(url=referer, status_code=303)
