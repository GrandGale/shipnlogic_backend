from pydantic import BaseModel, Field, EmailStr
from app.common.schemas import Token


class Admin(BaseModel):
    """The base admin model"""

    id: int = Field(description="The admin's ID")
    profile_picture_url: str = Field(description="The admin's profile picture URL")
    full_name: str = Field(description="The admin's full name")
    email: str = Field(description="The admin's email")
    phone_number: str = Field(description="The admin's phone number")
    permission: str = Field(description="Whether the admin is a super admin or not")
    added_by: str = Field(description="The admin that added this admin")


class AdminLogin(BaseModel):
    """The base admin login model"""

    admin: Admin = Field(description="The admin's details")
    tokens: Token = Field(description="The admin's auth tokens")


class AdminLoginCredential(BaseModel):
    """The base admin login credential model"""

    email: EmailStr = Field(
        description="The admin's email address", examples=["admin@shipnlogic.com"]
    )
    password: str = Field(description="The admin's password", examples=["admin"])
    remember_me: bool = Field(
        description="Expire refresh token in 24hrs if true else expire in 72hrs",
        default=False,
    )
