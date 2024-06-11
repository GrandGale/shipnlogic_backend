from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.common.schemas import PaginationSchema, Token


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


class UserConfiguration(BaseModel):
    """The base user configuration model"""

    id: int = Field(description="The user configuration ID")
    notification_email: bool = Field(description="The user email notification status")
    notification_inapp: bool = Field(description="The user in-app notification status")


class UserNotification(BaseModel):
    """The base schema for user notifications"""

    id: int = Field(description="The ID of the notification")
    content: str = Field(description="The notification message")
    is_read: bool = Field(description="The notification read status")
    created_at: datetime = Field(description="The notification created date")


class PaginatedUserNotification(BaseModel):
    """The base schema for paginated user notifications"""

    notifications: list[UserNotification] = Field(
        description="The list of user notifications"
    )
    unread: bool = Field(description="Indicates if there are unread notifications")
    meta: PaginationSchema = Field(description="The pagination details")


class Company(BaseModel):
    """The base company model"""

    id: int = Field(description="The company's ID")
    name: str = Field(description="The company's name")
    registration_number: str = Field(description="The company's registration number")
    email: str = Field(description="The company's email")
    phone: str = Field(description="The company's phone number")
    address: str = Field(description="The company's address")
    tax_identification_number: str = Field(
        description="The company's tax identification number"
    )
    is_verified: bool = Field(description="Whether the user is verified")
    permit_image_url: str = Field(description="The company's permit image URL")
    license_image_url: str = Field(description="The company's license image URL")
