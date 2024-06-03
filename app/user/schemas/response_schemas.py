from pydantic import Field
from app.common.schemas import ResponseSchema
from app.user.schemas.base_schemas import User, UserLogin


class UserResponse(ResponseSchema):
    """The user response model"""

    data: User = Field(description="The user's data")


class UserLoginResponse(ResponseSchema):
    """The user login response model"""

    data: UserLogin = Field(description="The user's details and auth tokens")
