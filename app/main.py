from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os

from app.database import connect_db, close_db
from app.routes import doctors, reviews, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Hospital Review System", lifespan=lifespan)

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(doctors.router)
app.include_router(reviews.router)
app.include_router(admin.router)
