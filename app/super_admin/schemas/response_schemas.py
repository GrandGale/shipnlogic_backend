from pydantic import Field

from app.common.schemas import ResponseSchema
from app.super_admin.schemas.base_schemas import Admin, AdminLogin


class AdminResponse(ResponseSchema):
    """The admin response model"""

    data: Admin = Field(description="The admin's data")


class AdminLoginResponse(ResponseSchema):
    """The admin login response model"""

    data: AdminLogin = Field(description="The admin's details and auth tokens")
