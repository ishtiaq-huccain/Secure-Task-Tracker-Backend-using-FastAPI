from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# ----------------
# Auth Schemas
# ----------------
class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ----------------
# Task Schemas
# ----------------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date
    status: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    due_date: date
    status: str
    owner_id: int

    class Config:
        orm_mode = True
