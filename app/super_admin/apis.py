from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, status
from app.common.security import verify_password, hash_password
from app.common.annotations import DatabaseSession, PaginationParams
from app.common.paginators import get_pagination_metadata, paginate
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


@router.get(
    "/notifications",
    summary="Get Admin Notification List",
    response_description="The list of the admin's notifications",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminNotificationListResponse,
)
async def admin_notifications(
    pagination: PaginationParams,
    current_admin: CurrentAdmin,
    db: DatabaseSession,
):
    """This endpoint returns a paginated list of the current logged in admin's notifications"""
    notifications_qs = db.query(models.AdminNotification).filter_by(
        admin_id=current_admin.id
    )
    paginated_notifications: list[models.AdminNotification] = paginate(
        qs=notifications_qs, page=pagination.page, size=pagination.size
    )
    return {
        "data": {
            "notifications": [
                {
                    "id": noti.id,
                    "content": noti.content,
                    "created_at": noti.created_at,
                    "is_read": noti.is_read,
                }
                for noti in paginated_notifications
            ],
            "unread": any(not noti.is_read for noti in paginated_notifications),
            "meta": get_pagination_metadata(
                qs=notifications_qs,
                count=len(paginated_notifications),
                page=pagination.page,
                size=pagination.size,
            ),
        }
    }


@router.put(
    "/notifications/read",
    summary="Mark Admin Notifications as Read",
    response_description="Notifications have been marked as read",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def admin_notification_read(current_admin: CurrentAdmin, db: DatabaseSession):
    """This endpoint marks all the admin's notifications as read"""

    db.query(models.AdminNotification).filter_by(
        admin_id=current_admin.id, is_read=False
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"data": {"message": "Notifications have been marked as read"}}


@router.post(
    "/password/confirm",
    summary="Confirm Admin's Password",
    response_description="Password Confirmed",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def admin_password_confirm(
    current_admin: CurrentAdmin,
    password: str = Body(description="The admin's password", min_length=1, embed=True),
):
    """This endpoints confirms the admin's password"""

    if verify_password(plain_password=password, hashed_password=current_admin.password):
        return {"data": {"is_correct": True}}
    return {"data": {"is_correct": False}}


@router.put(
    "/password/change",
    summary="Change Admin Password",
    response_description="The Admin's Details",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.AdminResponse,
)
async def admin_password_change(
    password_change: edit_schemas.AdminPasswordChange,
    current_admin: CurrentAdmin,
    db: DatabaseSession,
):
    """This endpoint changes the admin's password"""

    if verify_password(
        plain_password=password_change.old_password,
        hashed_password=current_admin.password,
    ):
        current_admin.password = hash_password(raw=password_change.new_password)
        db.commit()

        # Notifications
        await services.create_admin_notification(
            admin_id=current_admin.id,
            content="You have successfully changed your password",
            db=db,
        )
        return {"data": current_admin}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect Password"
    )
