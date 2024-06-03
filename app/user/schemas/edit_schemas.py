from pydantic import BaseModel, EmailStr, Field


class UserEdit(BaseModel):
    """This schema is used to edit the user's details"""

    profile_picture_url: str | None = Field(
        description="The url of the image",
        min_length=1,
        default=None,
        examples=["https://example.com/image.jpg"],
    )
    full_name: str | None = Field(
        description="The user's ull name", min_length=1, default=None
    )


class UserPasswordChange(BaseModel):
    """This schema is used to change the user's password"""

    old_password: str = Field(description="The user's old password", min_length=1)
    new_password: str = Field(description="The user's new password", min_length=1)


class UserProfilePicture(BaseModel):
    """This schema is used to edit the user's profile picture"""

    profile_picture_url: str = Field(
        description="The url of the image",
        min_length=1,
        examples=["https://example.com/image.jpg"],
    )


class UserEmailChange(BaseModel):
    """This schema is used to change the user's email"""

    email: EmailStr = Field(
        description="The user's new email",
        min_length=1,
        examples=["user@shipnlogic.com"],
    )
    edit_token: str = Field(description="The user's edit token", min_length=1)



