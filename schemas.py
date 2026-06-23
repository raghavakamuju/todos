from pydantic import BaseModel


class TaskCreate(BaseModel):

    title: str

    completed: bool = False

    user_id: int

class TaskResponse(BaseModel):

    id: int

    title: str

    completed: bool

    class Config:
        from_attributes = True

class UserCreate(BaseModel):

    username: str

    email: str

    password: str

class LoginRequest(BaseModel):

    email: str

    password: str



class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    class Config:
        from_attributes = True