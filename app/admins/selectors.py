from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_db
from app.config.settings import get_settings
from app.admins import models
from app.user import security

settings = get_settings()


async def get_admin_by_id(admin_id: int, db: Session, raise_exception: bool = True):
    """This function returns an admin obj using it's id

    Args:
        admin_id (int): The admin's id
        db (Session): The database session
        raise_exception (bool, default=True): Raise HTTPException[404] when admin isn't found

    Raises:
        HTTPException[404]: Admin not found

    Returns:
        (models.Admin| None): The Admin obj or None
    """
    if obj := db.query(models.Admin).filter_by(id=admin_id).first():
        return obj
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )
    return None


async def get_admin_by_email(email: str, db: Session, raise_exception: bool = True):
    """This function returns an admin obj based on the admin's email

    Args:
        email (str): The admin's email
        db (Session): The database session
        raise_exception (bool, default=True): Raise a HTTPException[404] when admin isn't found

    Raises:
        HTTPException[404]: Admin not found

    Returns:
        (models.Admin, None): The admin obj or None
    """
    if obj := db.query(models.Admin).filter_by(email=email).first():
        return obj
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )
    return None


async def get_admin_refresh_token(admin_id: int, token: str, db: Session):
    """This function returns an admin's refresh token

    Args:
        admin_id (int): The admin's ID
        token (str): The admin's refresh token
        db (Session): The database session

    Returns:
        (models.AdminRefreshToken): The admin refresh token obj
    """
    obj = (
        db.query(models.AdminRefreshToken)
        .filter_by(admin_id=admin_id, token=token)
        .first()
    )
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    return obj


async def get_current_admin(
    token: str = Header(alias="Authorization"), db: Session = Depends(get_db)
):
    """This function returns the current admin based on the token provided"""
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
    admin_id = int(security.verify_user_access_token(token=token))
    if admin := await get_admin_by_id(admin_id=admin_id, db=db, raise_exception=False):
        return admin
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token type",
    )


async def get_admin_configuration_by_admin_id(admin_id: int, db: Session):
    """This function returns the admin configuration based on the admin's ID

    Args:
        admin_id (int): The admin's ID
        db (Session): The database session

    Returns:
        (models.AdminConfiguration): The Admin configuration obj
    """
    obj = db.query(models.AdminConfiguration).filter_by(admin_id=admin_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin Configuration for admin {admin_id} not found",
        )
    return obj
