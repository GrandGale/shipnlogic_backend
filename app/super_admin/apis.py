from fastapi import APIRouter, HTTPException, status

from app.common.annotations import DatabaseSession
from app.config.settings import get_settings
from app.super_admin import services
from app.super_admin.annotations import CurrentAdmin
from app.super_admin.schemas import (base_schemas, create_schemas,
                                     edit_schemas, response_schemas)
from app.user import security
from app.user import services as user_services

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
    await user_services.create_user_refresh_token(
        user_id=admin.id, token=refresh_token, db=db
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
