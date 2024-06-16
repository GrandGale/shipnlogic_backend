from pydantic import Field

from app.common.schemas import ResponseSchema
from app.super_admin.schemas.base_schemas import (
    Admin,
    AdminConfiguration,
    AdminLogin,
    PaginatedAdminNotification,
)


class AdminResponse(ResponseSchema):
    """The admin response model"""

    data: Admin = Field(description="The admin's data")


class AdminLoginResponse(ResponseSchema):
    """The admin login response model"""

    data: AdminLogin = Field(description="The admin's details and auth tokens")


class AdminConfigurationResponse(ResponseSchema):
    """This is the response schema for the admin configuration"""

    data: AdminConfiguration = Field(description="The admin's configuration")


class AdminNotificationListResponse(ResponseSchema):
    """This is the response schema for the admin notification list"""

    data: PaginatedAdminNotification = Field(
        description="The paginated list of admin notifications"
    )
