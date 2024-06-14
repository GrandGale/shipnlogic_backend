from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.super_admin import models

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
