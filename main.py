from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
import motor.motor_asyncio
from starlette.responses import JSONResponse


# SCHEMA
class Student(BaseModel):
    first_name: str
    last_name: str
    gender: str

class MultiInsertStudent(BaseModel):
    students: List[Student]


# setup mongo
# MONGO_DETAILS = "mongodb://localhost:27017"
MONGO_DETAILS = ""
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# connect to a database
database = client.test

# load up a collection
student_collection = database.get_collection("students")

app =FastAPI()

def student_helper(student: dict) -> dict:
    student.update({"_id": str(student["_id"])})
    return student

async def retrieve_students():
    return [student_helper(each) async for each in student_collection.find()]

@app.post("/data")
async def add_data(payload: MultiInsertStudent):
    compatible_json_student_data = jsonable_encoder(payload.dict()["students"])
    await student_collection.insert_many(compatible_json_student_data)
    students = await retrieve_students()
    return JSONResponse(content=students, status_code=201)

@app.get("/data", response_model=MultiInsertStudent)
async def get_data():
    students = await retrieve_students()
    return JSONResponse(content=students, status_code=200)