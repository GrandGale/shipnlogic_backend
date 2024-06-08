from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, status

from app.common.annotations import DatabaseSession, PaginationParams
from app.common.paginators import get_pagination_metadata, paginate
from app.common.schemas import ResponseSchema
from app.common.security import hash_password, verify_password
from app.config.settings import get_settings
from app.user import models, security, selectors, services
from app.user.annotations import CurrentUser
from app.user.schemas import (
    base_schemas,
    create_schemas,
    edit_schemas,
    response_schemas,
)

settings = get_settings()

router = APIRouter()


@router.post(
    "",
    summary="Create a new user",
    response_description="The created user's data",
    status_code=status.HTTP_201_CREATED,
    response_model=response_schemas.UserResponse,
)
async def user_create(user_in: create_schemas.UserCreate, db: DatabaseSession):
    """Create a new user"""
    created_user = await services.create_user(data=user_in, db=db)

    try:
        await services.create_user_configuration(user_id=created_user.id, db=db)
    except HTTPException as e:
        db.delete(created_user)
        db.commit()
        raise e

    # Send Notification
    await services.create_user_notification(
        user_id=created_user.id, content="Welcome to ShipNLogic :)", db=db
    )
    return {"data": created_user}


@router.post(
    "/login",
    summary="User Login",
    response_description="The user's details and tokens",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserLoginResponse,
)
async def user_login(
    credential_in: base_schemas.UserLoginCredential, db: DatabaseSession
):
    """User Login"""
    user = await services.login_user(data=credential_in, db=db)

    if credential_in.remember_me:
        expire_in = settings.REFRESH_TOKEN_EXPIRE_HOURS_LONG
    else:
        expire_in = settings.REFRESH_TOKEN_EXPIRE_HOURS

    refresh_token = security.generate_user_token(
        token_type="refresh", sub=f"USER-{user.id}", expire_in=expire_in
    )
    access_token = security.generate_user_token(
        token_type="access",
        sub=f"USER-{user.id}",
        expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await services.create_user_refresh_token(
        user_id=user.id, token=refresh_token, db=db
    )
    return {
        "data": {
            "user": user,
            "tokens": {"access_token": access_token, "refresh_token": refresh_token},
        }
    }


@router.put(
    "",
    summary="Edit User Details",
    response_description="The User's Details (Edited)",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserResponse,
)
async def user_edit(
    user_in: edit_schemas.UserEdit,
    user: CurrentUser,
    db: DatabaseSession,
):
    """This endpoint is used to edit the user's details"""
    user = await services.edit_user(user_id=user.id, data=user_in, db=db)
    return {"data": user}


@router.post(
    "/token",
    summary="Generate User Access Token",
    response_description="The user's access token",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def user_refresh_token(
    db: DatabaseSession,
    refresh_token: str = Body(
        description="The user's refresh token", min_length=1, embed=True
    ),
):
    """This endpoint generates a new access token for the user using the refresh token"""
    await selectors.get_user_refresh_token(token=refresh_token, db=db)
    user_id = security.verify_user_refresh_token(token=refresh_token)
    user = await selectors.get_user_by_id(user_id=user_id, db=db)
    user.last_login = datetime.now()
    db.commit()
    return {
        "data": {
            "access_token": security.generate_user_token(
                token_type="access",
                sub=f"USER-{user_id}",
                expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        }
    }


@router.delete(
    "/logout",
    summary="Logout User",
    response_description="User has been logged out",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def user_logout(current_user: CurrentUser, db: DatabaseSession):
    """This endpoint logs out the current user by deleting all their refresh tokens"""
    db.query(models.UserRefreshToken).filter_by(user_id=current_user.id).delete()
    db.commit()
    return {"data": {"message": "User has been logged out"}}


@router.get(
    "/me",
    summary="Get user details",
    response_description="The user's details",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserResponse,
)
def user_me(user: CurrentUser):
    """The endpoint returns the details of the current logged in user"""
    return {"data": user}


@router.get(
    "/configurations",
    summary="Get User Configuration",
    response_description="The user's configuration",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserConfigurationResponse,
)
async def user_configurations(current_user: CurrentUser, db: DatabaseSession):
    """This endpoint returns the user's configurations"""

    return {
        "data": await selectors.get_user_configuration_by_user_id(
            user_id=current_user.id, db=db
        )
    }


@router.put(
    "/configurations",
    summary="Edit User Configurations",
    response_description="The user's configuration (new)",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserConfigurationResponse,
)
async def user_configurations_edit(
    configuration_in: edit_schemas.UserConfigurationEdit,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """This endpoint returns the user's configurations"""
    configurations = await selectors.get_user_configuration_by_user_id(
        user_id=current_user.id, db=db
    )

    # Update configurations
    for field, value in configuration_in.model_dump().items():
        setattr(configurations, field, value)
    db.commit()

    return {"data": configurations}


@router.get(
    "/notifications",
    summary="Get User Notification List",
    response_description="The list of the user's notifications",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserNotificationListResponse,
)
async def user_notifications(
    pagination: PaginationParams,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """This endpoint returns a paginated list of the current logged in user's notifications"""
    notifications_qs = db.query(models.UserNotification).filter_by(
        user_id=current_user.id
    )
    paginated_notifications: list[models.UserNotification] = paginate(
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
    summary="Mark User Notifications as Read",
    response_description="Notifications have been marked as read",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def user_notification_read(current_user: CurrentUser, db: DatabaseSession):
    """This endpoint marks all the user's notifications as read"""

    db.query(models.UserNotification).filter_by(
        user_id=current_user.id, is_read=False
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"data": {"message": "Notifications have been marked as read"}}


@router.post(
    "/password/confirm",
    summary="Confirm User's Password",
    response_description="Password Confirmed",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSchema,
)
async def user_password_confirm(
    current_user: CurrentUser,
    password: str = Body(description="The user's password", min_length=1, embed=True),
):
    """This endpoints confirms the user's password"""

    if verify_password(plain_password=password, hashed_password=current_user.password):
        return {"data": {"is_correct": True}}
    return {"data": {"is_correct": False}}


@router.put(
    "/password/change",
    summary="Change User Password",
    response_description="The User's Details",
    status_code=status.HTTP_200_OK,
    response_model=response_schemas.UserResponse,
)
async def user_password_change(
    password_change: edit_schemas.UserPasswordChange,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """This endpoint changes the user's password"""

    if verify_password(
        plain_password=password_change.old_password,
        hashed_password=current_user.password,
    ):
        current_user.password = hash_password(raw=password_change.new_password)
        db.commit()

        # Notifications
        await services.create_user_notification(
            user_id=current_user.id,
            content="You have successfully changed your password",
            db=db,
        )
        return {"data": current_user}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect Password"
    )
