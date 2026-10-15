from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.models import student
from app.models import user
from app.routers import students
from app.routers import auth
from app.routers import tasks


app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Student API is running"
    }


app.include_router(students.router)
app.include_router(auth.router)
app.include_router(tasks.router)