from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """The User creation model"""


    full_name: str = Field(
        description="The user's full name",
        min_length=1,
        max_length=255,
        examples=["Alice"],
    )
    email: EmailStr = Field(
        description="The user's email", min_length=1, examples=["user@shipnlogic.com"]
    )
    exception_alert_email: EmailStr = Field(
        description="The user's exception alert email",
        min_length=1,
        examples=["user@shipnlogic.com"],
    )
    password: str = Field(
        description="The user's password",
        min_length=1,
        examples=["admin"],
    )
