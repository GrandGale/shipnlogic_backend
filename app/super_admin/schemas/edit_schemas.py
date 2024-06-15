from typing import Literal

from pydantic import BaseModel, Field


class AdminEdit(BaseModel):
    """This schema is used to edit the admin's details"""

    profile_picture_url: str | None = Field(
        description="The url of the image",
        min_length=1,
        default=None,
        examples=["https://example.com/image.jpg"],
    )
    full_name: str | None = Field(
        description="The admin's full name", min_length=1, default=None
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


class AdminConfigurationEdit(BaseModel):
    """The edit schema for admin configurations"""

    notification_email: bool = Field(description="The admin email notification status")
    notification_inapp: bool = Field(description="The admin in-app notification status")
