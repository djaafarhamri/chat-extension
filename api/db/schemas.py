from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class MessageSend(BaseModel):
    message: str
