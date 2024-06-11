from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """The User creation model"""

    full_name: str = Field(
        description="The user's full name",
        min_length=1,
        max_length=255,
        examples=["Alice"],
    )
    email: EmailStr = Field(
        description="The user's email", min_length=1, examples=["user@shipnlogic.com"]
    )
    exception_alert_email: EmailStr = Field(
        description="The user's exception alert email",
        min_length=1,
        examples=["user@shipnlogic.com"],
    )
    password: str = Field(
        description="The user's password",
        min_length=1,
        examples=["admin"],
    )


class CompanyCreate(BaseModel):
    """The Company creation model"""

    name: str = Field(
        description="The company's name",
        min_length=1,
        max_length=255,
        examples=["ShipnLogic"],
    )
    registration_number: str = Field(
        description="The company's registration number",
        min_length=1,
        examples=["12345678"],
    )
    email: EmailStr = Field(
        description="The company's email",
        min_length=1,
        examples=["user@shipnlogic.com"],
    )
    phone: str = Field(
        description="The company's phone number",
        min_length=1,
        examples=["+234567890123"],
    )
    address: str = Field(
        description="The company's address",
        min_length=1,
        examples=["123, ShipnLogic Street, Lagos, Nigeria"],
    )
    tax_identification_number: str = Field(
        description="The company's tax identification number",
        min_length=1,
        examples=["12345678"],
    )
