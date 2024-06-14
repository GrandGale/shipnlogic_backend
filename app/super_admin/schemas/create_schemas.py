from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class AdminCreate(BaseModel):
    """The Admin creation model"""

    full_name: str = Field(
        description="The admin's full name",
        min_length=1,
        max_length=255,
        examples=["Alice"],
    )
    email: EmailStr = Field(
        description="The user's email", min_length=1, examples=["user@shipnlogic.com"]
    )
    phone_number: str = Field(
        description="The admin's phone number",
        min_length=1,
        examples=["+234567890123"],
    )
    gender: Literal["MALE", "FEMALE"] = Field(
        description="The admin's gender",
        pattern=r"MALE|FEMALE",
        examples=["MALE", "FEMALE"],
    )
    permission: Literal["SUPER_ADMIN", "ADMIN"] = Field(
        description="The admin's permission",
        pattern=r"SUPER_ADMIN|ADMIN",
        examples=["SUPER_ADMIN", "ADMIN"],
    )
    password: str = Field(
        description="The user's password",
        min_length=1,
        examples=["admin"],
    )
