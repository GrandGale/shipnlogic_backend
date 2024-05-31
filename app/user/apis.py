from fastapi import APIRouter
from fastapi import APIRouter, Body, HTTPException, status
from app.user.schemas import (
    response_schemas,
    create_schemas,
    base_schemas,
    edit_schemas,
)
from app.common.annotations import DatabaseSession
from app.user import services, security
from app.config.settings import get_settings
from app.user.annotations import CurrentUser

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
        token_type="refresh",
        sub=f"USER-{user.id}",
        expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{user.id}", expire_in=expire_in
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
