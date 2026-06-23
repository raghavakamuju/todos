from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException

import models
from sqlalchemy.orm import Session
from schemas import UserResponse
import crud
import models 
from schemas import UserCreate
from fastapi.security import OAuth2PasswordBearer
from database import SessionLocal
from database import engine

from schemas import (
    TaskCreate,
    TaskResponse
)
from schemas import LoginRequest
from auth import (
    verify_password,
    create_access_token,
    verify_token
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

app = FastAPI()

models.Base.metadata.create_all(
    bind=engine
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload.get("sub")

    user = crud.get_user(
        db,
        int(user_id)
    )

    return user

@app.get("/")
def home():

    return {
        "message": "Task Manager API Running"
    }


@app.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = crud.get_user_by_email(
        db,
        login_data.email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(models.User).all()

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db)
):

    updated_user = crud.update_user(
        db,
        user_id,
        user
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = crud.get_user(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@app.post(
    "/users",
    response_model=UserResponse
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    return crud.create_user(
        db,
        user
    )


@app.get("/me", response_model=UserResponse)
def get_me(
    current_user = Depends(
        get_current_user
    )
):

    return current_user

@app.get("/users/{user_id}/tasks",
    response_model=list[TaskResponse]
)
def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = crud.get_user(
        db,
        user_id
    )

    return user.tasks

@app.get(
    "/tasks",
    response_model=list[TaskResponse]
)
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # return only tasks belonging to the authenticated user
    return [t for t in crud.get_tasks(db) if t.user_id == current_user.id]


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)


def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = crud.get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.post(
    "/tasks",
    response_model=TaskResponse
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # ignore client-supplied user_id and associate the task with the current user
    task_for_db = TaskCreate(
        title=task.title,
        completed=task.completed,
        user_id=current_user.id
    )

    return crud.create_task(
        db,
        task_for_db
    )


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    db_task = crud.get_task(db, task_id)

    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_task = crud.update_task(
        db,
        task_id,
        task
    )

    return updated_task


@app.delete(
    "/users/{user_id}",
    response_model=UserResponse
)

def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    deleted_user = crud.delete_user(
        db,
        user_id
    )

    if not deleted_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }       

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    db_task = crud.get_task(db, task_id)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    deleted_task = crud.delete_task(db, task_id)

    return {
        "message": "Task deleted successfully"
    }


@app.get("/users/{user_id}/tasks")
def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user.tasks