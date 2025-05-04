from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: Optional[str] = None
    isActive: Optional[bool] = True
    isSuperUser: Optional[bool] = False
    name: Optional[str] = None


class UserIn(UserBase):
    email: str
    name: str
    password: str


class UserOut(UserBase):
    id: str
