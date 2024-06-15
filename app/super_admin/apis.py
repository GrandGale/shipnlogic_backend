from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, status

from app.common.annotations import DatabaseSession
from app.common.schemas import ResponseSchema
from app.config.settings import get_settings
from app.super_admin import models, selectors, services
from app.super_admin.annotations import CurrentAdmin
from app.super_admin.schemas import (
    base_schemas,
    create_schemas,
    edit_schemas,
    response_schemas,
)
from app.user import security

settings = get_settings()

router = APIRouter()


@router.post(
    "",
    summary="Create a new Admin",
    response_description="The created admin's data",
    status_code=status.HTTP_201_CREATED,
    response_model=response_schemas.AdminResponse,
)
async def admin_create(admin_in: create_schemas.AdminCreate, db: DatabaseSession):
    """Create a new admin"""
    created_admin = await services.create_admin(data=admin_in, db=db)

    try:
        await services.create_admin_configuration(admin_id=created_admin.id, db=db)
    except HTTPException as e:
        db.delete(created_admin)
        db.commit()
        raise e

    # Send Notification
    await services.create_admin_notification(
        admin_id=created_admin.id, content="Welcome to ShipNLogic :)", db=db
    )
    return {"data": created_admin}


@router.post(
    "/login",
    summary="admin Login",
    response_description="The admin's details and tokens",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminLoginResponse,
)
async def admin_login(
    credential_in: base_schemas.AdminLoginCredential, db: DatabaseSession
):
    """admin Login"""
    admin = await services.login_admin(data=credential_in, db=db)

    if credential_in.remember_me:
        expire_in = settings.REFRESH_TOKEN_EXPIRE_HOURS_LONG
    else:
        expire_in = settings.REFRESH_TOKEN_EXPIRE_HOURS

    refresh_token = security.generate_user_token(
        token_type="refresh", sub=f"ADMIN-{admin.id}", expire_in=expire_in
    )
    access_token = security.generate_user_token(
        token_type="access",
        sub=f"ADMIN-{admin.id}",
        expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await services.create_admin_refresh_token(
        admin_id=admin.id, token=refresh_token, db=db
    )
    return {
        "data": {
            "admin": admin,
            "tokens": {"access_token": access_token, "refresh_token": refresh_token},
        }
    }


@router.put(
    "",
    summary="Edit Admin Details",
    response_description="The Admin's Details (Edited)",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminResponse,
)
async def admin_edit(
    admin_in: edit_schemas.AdminEdit,
    admin: CurrentAdmin,
    db: DatabaseSession,
):
    """This endpoint is used to edit the admin's details"""
    admin = await services.edit_admin(admin_id=admin.id, data=admin_in, db=db)
    return {"data": admin}


@router.post(
    "/token",
    summary="Generate Admin Access Token",
    response_description="The admin's access token",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def user_refresh_token(
    db: DatabaseSession,
    refresh_token: str = Body(
        description="The Admin's refresh token", min_length=1, embed=True
    ),
):
    """This endpoint generates a new access token for the admin using the refresh token"""
    admin_id = security.verify_user_refresh_token(token=refresh_token)
    await selectors.get_admin_refresh_token(
        admin_id=admin_id, token=refresh_token, db=db
    )
    admin = await selectors.get_admin_by_id(admin_id=admin_id, db=db)
    admin.last_login = datetime.now()
    db.commit()
    return {
        "data": {
            "access_token": security.generate_user_token(
                token_type="access",
                sub=f"ADMIN-{admin_id}",
                expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        }
    }


@router.delete(
    "/logout",
    summary="Logout Admin",
    response_description="Admin has been logged out",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def admin_logout(admin_user: CurrentAdmin, db: DatabaseSession):
    """This endpoint logs out the current admin by deleting all their refresh tokens"""
    db.query(models.AdminRefreshToken).filter_by(admin_id=admin_user.id).delete()
    db.commit()
    return {"data": {"message": "Admin has been logged out"}}


@router.get(
    "/me",
    summary="Get admin details",
    response_description="The admin's details",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminResponse,
)
async def admin_me(admin: CurrentAdmin):
    """The endpoint returns the details of the current logged in admin"""
    return {"data": admin}


@router.get(
    "/configurations",
    summary="Get Admin Configuration",
    response_description="The admin's configuration",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminConfigurationResponse,
)
async def admin_configurations(current_admin: CurrentAdmin, db: DatabaseSession):
    """This endpoint returns the admin's configurations"""

    return {
        "data": await selectors.get_admin_configuration_by_admin_id(
            admin_id=current_admin.id, db=db
        )
    }


@router.put(
    "/configurations",
    summary="Edit Admin Configurations",
    response_description="The admin's configuration (new)",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminConfigurationResponse,
)
async def admin_configurations_edit(
    configuration_in: edit_schemas.AdminConfigurationEdit,
    current_admin: CurrentAdmin,
    db: DatabaseSession,
):
    """This endpoint returns the admin's configurations"""
    configurations = await selectors.get_admin_configuration_by_admin_id(
        admin_id=current_admin.id, db=db
    )

    # Update configurations
    for field, value in configuration_in.model_dump().items():
        setattr(configurations, field, value)
    db.commit()

    return {"data": configurations}
