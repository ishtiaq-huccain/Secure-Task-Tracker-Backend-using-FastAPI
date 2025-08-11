from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from . import models, schemas, auth
from .database import engine, get_db, Base
from .auth import hash_password, verify_password, create_access_token, get_current_user, require_admin

Base.metadata.create_all(bind=engine)

# OAuth2 Bearer setup for Swagger Authorize popup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Secure Task Tracker with JWT")

# ----------------
# Auth / User Endpoints
# ----------------
@app.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    user = models.User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=schemas.Token)
def login(form_data: schemas.LoginSchema, db: Session = Depends(get_db)):
    """
    Accepts email/password JSON body and returns JWT token.
    """
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ----------------
# Task Endpoints (user-scoped)
# ----------------
@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = models.Task(
        title=task_in.title,
        description=task_in.description or "",
        due_date=task_in.due_date,
        status=task_in.status or "pending",
        owner_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=List[schemas.TaskOut])
def list_tasks(
    skip: int = 0,
    limit: int = Query(10, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if status:
        q = q.filter(models.Task.status == status)
    if search:
        q = q.filter(models.Task.title.contains(search) | models.Task.description.contains(search))
    tasks = q.offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, update: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if update.title is not None:
        task.title = update.title
    if update.description is not None:
        task.description = update.description
    if update.due_date is not None:
        task.due_date = update.due_date
    if update.status is not None:
        task.status = update.status
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

# ----------------
# Admin Endpoints
# ----------------
@app.get("/admin/tasks", response_model=List[schemas.TaskOut])
def admin_list_all_tasks(skip: int = 0, limit: int = Query(50, le=500), db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    return db.query(models.Task).offset(skip).limit(limit).all()


@app.get("/admin/users", response_model=List[schemas.UserOut])
def admin_list_users(skip: int = 0, limit: int = Query(50, le=500), db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    return db.query(models.User).offset(skip).limit(limit).all()


@app.delete("/admin/users/{user_id}", status_code=200)
def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"user {user_id} deleted"}


@app.put("/admin/users/{user_id}/role", response_model=schemas.UserOut)
def admin_change_role(user_id: int, new_role: dict, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    role = new_role.get("role")
    if role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
