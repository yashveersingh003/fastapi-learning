from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Student(Base):

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    course = Column(String, nullable=False)

    age = Column(Integer, nullable=False)