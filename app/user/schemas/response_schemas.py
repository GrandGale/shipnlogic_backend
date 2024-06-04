from pydantic import Field
from app.common.schemas import ResponseSchema
from app.user.schemas.base_schemas import User, UserLogin, UserConfiguration, PaginatedUserNotification


class UserResponse(ResponseSchema):
    """The user response model"""

    data: User = Field(description="The user's data")


class UserLoginResponse(ResponseSchema):
    """The user login response model"""

    data: UserLogin = Field(description="The user's details and auth tokens")


class UserConfigurationResponse(ResponseSchema):
    """This is the response schema for the user configuration"""

    data: UserConfiguration = Field(description="The user's configuration")

class UserNotificationListResponse(ResponseSchema):
    """This is the response schema for the user notification list"""

    data: PaginatedUserNotification = Field(
        description="The paginated list of user notifications"
    )
