from typing import Optional

from fastapi import HTTPException
from odetam import DetaModel
from pydantic import Field, EmailStr, BaseModel


class UserNotFound(BaseException):
    pass


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., title="Email", description="User email address")


class User(DetaModel):
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "Rick Henry",
                "email": "rhenry@trentonmusicmakers.org",
                "admin": True,
            }
        }

    name: str = Field("", title="Full Name", description="User's full name")
    email: EmailStr = Field(..., title="Email", description="User's email address")
    admin: bool = Field(
        False,
        title="Admin",
        description="Whether or not a user is an administrator. Defaults to False.",
    )
    disabled: bool = Field(
        False, title="Disabled", description="Whether an account is disabled or not"
    )


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, title="Full Name", description="User's full name")
    email: EmailStr = Field(None, title="Email", description="User's email address")


class UserUpdateResponse(BaseModel):
    user: User
    message: str


async def get_user_by_email(email: str) -> Optional[User]:
    # noinspection PyTypeChecker
    found = User.query(User.email == email.lower())
    if not found:
        return None
    return found[0]


async def create_user_from_email(email: str) -> User:
    user = User(email=email)
    user.save()
    return user
