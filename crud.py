from sqlalchemy.orm import Session

from models import Task
from schemas import TaskCreate
from models import User
from auth import hash_password
from schemas import UserCreate

def delete_user(
    db: Session,
    user_id: int
):

    db_user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not db_user:
        return None

    db.delete(db_user)

    db.commit()

    return db_user      

def get_user_by_email(
    db: Session,
    email: str
):

    return db.query(User).filter(
        User.email == email
    ).first()

def create_user(
    db: Session,
    user: UserCreate
):

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user

def get_user(
    db: Session,
    user_id: int
):

    return db.query(User).filter(
        User.id == user_id
    ).first()

def get_tasks(db: Session):

    return db.query(Task).all()


def get_task(db: Session, task_id: int):

    return db.query(Task).filter(
        Task.id == task_id
    ).first()


def create_task(
    db: Session,
    task: TaskCreate
):

    db_task = Task(
        title=task.title,
        completed=task.completed,
        user_id=task.user_id

    )

    db.add(db_task)

    db.commit()

    db.refresh(db_task)

    return db_task

def update_user(
    db: Session,
    user_id: int,
    user: UserCreate
):

    db_user = db.query(User).filter(
        User.id == user_id
    ).with_for_update().first()

    if not db_user:
        return None

    db_user.username = user.username
    db_user.email = user.email

    db.commit()

    db.refresh(db_user)

    return db_user

def update_task(
    db: Session,
    task_id: int,
    task: TaskCreate
):

    db_task = db.query(Task).filter(
        Task.id == task_id
    ).with_for_update().first()

    if not db_task:
        return None

    db_task.title = task.title
    db_task.completed = task.completed

    db.commit()

    db.refresh(db_task)

    return db_task


def delete_task(
    db: Session,
    task_id: int
):

    db_task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not db_task:
        return None

    db.delete(db_task)

    db.commit()

    return db_task