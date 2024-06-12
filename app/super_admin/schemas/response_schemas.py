from pydantic import Field

from app.common.schemas import ResponseSchema
from app.super_admin.schemas.base_schemas import Admin


class AdminResponse(ResponseSchema):
    """The admin response model"""

    data: Admin = Field(description="The user's data")
