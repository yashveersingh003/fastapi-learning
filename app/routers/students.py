from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.student import Student

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# =========================
# REQUEST SCHEMAS
# =========================

class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    course: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=16, le=100)


class StudentUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    course: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=16, le=100)


class StudentPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    course: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    age: int | None = Field(
        default=None,
        ge=16,
        le=100
    )


# =========================
# RESPONSE SCHEMA
# =========================

class StudentResponse(BaseModel):
    id: int
    name: str
    course: str
    age: int

    model_config = ConfigDict(from_attributes=True)


# =========================
# GET ALL STUDENTS
# =========================

@router.get("/", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# =========================
# GET ONE STUDENT
# =========================

@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# =========================
# CREATE STUDENT
# =========================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    new_student = Student(
        name=student.name,
        course=student.course,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# =========================
# PUT - FULL UPDATE
# =========================

@router.put(
    "/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.name = student_data.name
    student.course = student_data.course
    student.age = student_data.age

    db.commit()
    db.refresh(student)

    return student


# =========================
# PATCH - PARTIAL UPDATE
# =========================

@router.patch(
    "/{student_id}",
    response_model=StudentResponse
)
def patch_student(
    student_id: int,
    student_data: StudentPatch,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    update_data = student_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student


# =========================
# DELETE STUDENT
# =========================

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }