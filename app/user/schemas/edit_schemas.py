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
        description="The user's full name", min_length=1, default=None
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


class UserConfigurationEdit(BaseModel):
    """The edit schema for user configurations"""

    notification_email: bool = Field(description="The user email notification status")
    notification_inapp: bool = Field(description="The user in-app notification status")


class CompanyEdit(BaseModel):
    """This schema is used to edit the company's details"""

    name: str | None = Field(
        description="The company's name", min_length=1, default=None
    )
    registration_number: str | None = Field(
        description="The company's registration number", min_length=1, default=None
    )
    email: EmailStr | None = Field(
        description="The company's email", min_length=1, default=None
    )
    phone: str | None = Field(
        description="The company's phone number", min_length=1, default=None
    )
    address: str | None = Field(
        description="The company's address", min_length=1, default=None
    )
    tax_identification_number: str | None = Field(
        description="The company's tax identification number",
        min_length=1,
        default=None,
    )
    permit_image_url: str | None = Field(
        description="The company's permit image URL",
        min_length=1,
        default=None,
    )
    license_image_url: str | None = Field(
        description="The company's license image URL",
        min_length=1,
        default=None,
    )
