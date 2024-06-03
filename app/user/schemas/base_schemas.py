from pydantic import BaseModel, EmailStr, Field

from app.common.schemas import Token


class User(BaseModel):
    """The base user model"""

    id: int = Field(description="The user's ID")
    profile_picture_url: str = Field(description="The user's profile picture URL")
    full_name: str = Field(description="The user's full name")
    email: str = Field(description="The user's email")
    exception_alert_email: str = Field(description="The user's exception alert email")
    is_active: bool = Field(description="Whether the user is active")
    is_verified: bool = Field(description="Whether the user is verified")


class UserLogin(BaseModel):
    """The base user login model"""

    user: User = Field(description="The user's details")
    tokens: Token = Field(description="The user's auth tokens")


class UserLoginCredential(BaseModel):
    """The base user login credential model"""

    email: EmailStr = Field(
        description="The user's email address", examples=["user@shipnlogic.com"]
    )
    password: str = Field(description="The user's password", examples=["admin"])
    remember_me: bool = Field(
        description="Expire refresh token in 24hrs if true else expire in 72hrs",
        default=False,
    )
