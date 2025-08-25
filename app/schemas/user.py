"""User-related Pydantic schemas.

Defines simple models for creating and returning user data through the API.
Passwords should only be provided in write schemas (e.g., UserCreate) and
never exposed in public read endpoints unless intentionally required.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    """Common user fields."""
    name: str
    email: str


class UserCreate(UserBase):
    """Schema used when creating a new user (includes password)."""
    password: str
    role: Optional[str] = "user"


class UserRead(UserBase):
    """Schema returned by the API to represent a stored user."""
    id: int
    password: str
    role: str
    model_config = ConfigDict(from_attributes=True)
