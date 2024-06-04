from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_db
from app.config.settings import get_settings
from app.user import models, security

settings = get_settings()


async def get_user_by_id(user_id: int, db: Session, raise_exception: bool = True):
    """This function returns a user obj using it's id
F
    Args:
        user_id (int): The user's id
        db (Session): The database session
        raise_exception (bool, default=True): Raise HTTPException[404] when user isn't found

    Raises:
        HTTPException[404]: User not found

    Returns:
        (models.User| None): The User obj or None
    """
    if obj := db.query(models.User).filter_by(id=user_id).first():
        return obj
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return None


async def get_user_configuration_by_user_id(user_id: int, db: Session):
    """This function returns the user configuration based on the user's ID

    Args:
        user_id (int): The user's ID
        db (Session): The database session

    Returns:
        (models.UserConfiguration): The User configuration obj
    """
    obj = db.query(models.UserConfiguration).filter_by(user_id=user_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User Configuration for user {user_id} not found",
        )
    return obj


async def get_user_by_email(email: str, db: Session, raise_exception: bool = True):
    """This function returns a user obj based on the user's email

    Args:
        email (str): The user's email
        db (Session): The database session
        raise_exception (bool, default=True): Raise a HTTPException[404] when user isn't found

    Raises:
        HTTPException[404]: User not found

    Returns:
        (models.User, None): The user obj or None
    """
    if obj := db.query(models.User).filter_by(email=email).first():
        return obj
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return None


async def get_current_user(
    token: str = Header(alias="Authorization"), db: Session = Depends(get_db)
):
    """This function returns the current user based on the token provided"""
    try:
        token_type, token = token.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if token_type != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user_id = int(security.verify_user_access_token(token=token))
    if user := await get_user_by_id(user_id=user_id, db=db, raise_exception=False):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token type",
    )


async def get_user_refresh_token(user_id: int, token: str, db: Session):
    """This function returns a user refresh token

    Args:
        user_id (int): The user's ID
        token (str): The user's refresh token
        db (Session): The database session

    Returns:
        (models.UserRefreshToken): The user refresh token obj
    """
    obj = (
        db.query(models.UserRefreshToken)
        .filter_by(user_id=user_id, token=token)
        .first()
    )
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    return obj
