from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.common.schemas import PaginationSchema
from app.common.schemas import Token


class Admin(BaseModel):
    """The base admin model"""

    id: int = Field(description="The admin's ID")
    profile_picture_url: str = Field(description="The admin's profile picture URL")
    full_name: str = Field(description="The admin's full name")
    email: str = Field(description="The admin's email")
    phone_number: str = Field(description="The admin's phone number")
    permission: str = Field(description="Whether the admin is a super admin or not")


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


class AdminConfiguration(BaseModel):
    """The base admin configuration model"""

    id: int = Field(description="The admin configuration ID")
    notification_email: bool = Field(description="The admin email notification status")
    notification_inapp: bool = Field(description="The admin in-app notification status")


class AdminNotification(BaseModel):
    """The base schema for admiin notifications"""

    id: int = Field(description="The ID of the notification")
    content: str = Field(description="The notification message")
    is_read: bool = Field(description="The notification read status")
    created_at: datetime = Field(description="The notification created date")


class PaginatedAdminNotification(BaseModel):
    """The base schema for paginated admin notifications"""

    notifications: list[AdminNotification] = Field(
        description="The list of admin notifications"
    )
    unread: bool = Field(description="Indicates if there are unread notifications")
    meta: PaginationSchema = Field(description="The pagination details")
