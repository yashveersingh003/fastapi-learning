from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Student(BaseModel):
    name: str
    course: str
    age: int


students = [
    {
        "id": 1,
        "name": "Rahul",
        "course": "CSE",
        "age": 21
    },
    {
        "id": 2,
        "name": "Aman",
        "course": "ECE",
        "age": 22
    }
]


@app.get("/")
def home():
    return {"message": "Student API is running"}


@app.get("/students")
def get_students():
    return students


@app.get("/students/{student_id}")
def get_student(student_id: int):

    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


@app.post(
    "/students",
    status_code=status.HTTP_201_CREATED
)
def create_student(student: Student):

    new_id = len(students) + 1

    new_student = {
        "id": new_id,
        "name": student.name,
        "course": student.course,
        "age": student.age
    }

    students.append(new_student)

    return new_student

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):

    for existing_student in students:

        if existing_student["id"] == student_id:

            existing_student["name"] = student.name
            existing_student["course"] = student.course
            existing_student["age"] = student.age

            return existing_student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    for student in students:

        if student["id"] == student_id:

            students.remove(student)

            return {
                "message": "Student deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )