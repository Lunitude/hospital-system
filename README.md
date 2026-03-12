# 🏥 MedCare Hospital Review System

A full-stack hospital doctor review management system built with FastAPI, MongoDB, and TailwindCSS.

---

## 📁 Project Structure

```
hospital_system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # MongoDB connection + admin seed
│   ├── models.py            # Pydantic models & specialty list
│   └── routes/
│       ├── __init__.py
│       ├── doctors.py       # Public doctor listing & profile routes
│       ├── reviews.py       # Review submission routes
│       └── admin.py         # Admin auth + management routes
├── templates/
│   ├── base.html            # Public layout
│   ├── admin_base.html      # Admin sidebar layout
│   ├── index.html           # Doctor listing (/)
│   ├── doctor.html          # Doctor profile (/doctor/{id})
│   ├── review.html          # Submit review (/review/{doctor_id})
│   ├── admin_login.html     # Admin login (/admin/login)
│   ├── admin_dashboard.html # Dashboard (/admin/dashboard)
│   ├── admin_add_doctor.html# Add doctor (/admin/add-doctor)
│   └── admin_manage_reviews.html # Manage reviews (/admin/manage-reviews)
├── static/
│   └── uploads/             # Uploaded doctor photos (auto-created)
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.9+
- MongoDB running locally on port 27017
  - Install: https://www.mongodb.com/try/download/community
  - Start on macOS: `brew services start mongodb-community`
  - Start on Linux: `sudo systemctl start mongod`
  - Start on Windows: Run as service or `mongod` in terminal

---

## 🚀 Setup & Run

### 1. Navigate to project directory
```bash
cd hospital_system
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the server
```bash
uvicorn app.main:app --reload
```

### 5. Open in browser
```
http://localhost:8000
```

---

## 🔐 Admin Credentials

Default admin login (auto-created on first run):
- **Username:** `admin`
- **Password:** `admin123`

> Change these in `app/database.py` for production use.

---

## 📄 Pages

| Route | Description |
|-------|-------------|
| `/` | Doctor listing with specialty filter |
| `/doctor/{id}` | Doctor profile with reviews & rating breakdown |
| `/review/{doctor_id}` | Patient review submission form |
| `/admin/login` | Admin login page |
| `/admin/dashboard` | Admin overview: doctors & recent reviews |
| `/admin/add-doctor` | Add a new doctor with optional photo |
| `/admin/manage-reviews` | View and delete reviews, filter by doctor |
| `/admin/logout` | Sign out |

---

## ✨ Features

- 🩺 **Doctor Management** — Add/delete doctors with name, specialty, optional photo
- ⭐ **Star Rating System** — Interactive 1–5 star rating with auto-calculated averages
- 💬 **Patient Reviews** — Submit reviews with name, rating, and optional feedback
- 🔍 **Specialty Filtering** — Filter/sort doctors by medical specialty
- 🔐 **Secure Admin** — JWT cookie-based admin authentication
- 📊 **Admin Dashboard** — Stats, doctor list, recent reviews at a glance
- 🖼️ **Image Uploads** — Support for JPG/PNG/WEBP doctor profile photos
- 📱 **Responsive Design** — Works on mobile, tablet, and desktop
