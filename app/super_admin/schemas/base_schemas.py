from pydantic import BaseModel, Field


class Admin(BaseModel):
    """The base admin model"""

    id: int = Field(description="The admin's ID")
    profile_picture_url: str = Field(description="The admin's profile picture URL")
    full_name: str = Field(description="The admin's full name")
    email: str = Field(description="The admin's email")
    phone_number: str = Field(description="The admin's phone number")
    permission: str = Field(description="Whether the admin is a super admin or not")
    added_by: str = Field(description="The admin that added this admin")
