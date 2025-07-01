from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserRead(UserBase):
    id: int
    password: str
    role: str
    model_config = ConfigDict(from_attributes=True)
