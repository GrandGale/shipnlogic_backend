from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.security import hash_password
from app.super_admin import models, selectors
from app.super_admin.schemas import create_schemas


async def create_admin(data: create_schemas.AdminCreate, db: Session):
    """This function creates a new admin

    Args:
        data (create_schemas.AdminCreate): The admin's data
        db (Session): The database session

    Raises:
        HTTPException[400]: Admin with email exists

    Returns:
        models.Admin: The created admin obj
    """
    # Validate unique email
    if db.query(models.Admin).filter_by(email=data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Admin with email {data.email} exists",
        )

    obj = models.Admin(**data.model_dump())
    obj.password = hash_password(raw=data.password)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def create_admin_configuration(admin_id: int, db: Session):
    """This function creates the admin's configuration obj

    Args:
        admin_id (int): The admin's ID
        db (Session): The database session

    Returns:
        models.AdminConfiguration: The created admin configuration obj
    """
    await selectors.get_admin_by_id(admin_id=admin_id, db=db)
    if db.query(models.AdminConfiguration).filter_by(admin_id=admin_id).first():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"admin configuration for admin {admin_id} already exists",
        )
    obj = models.AdminConfiguration(admin_id=admin_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def create_admin_notification(admin_id: int, content: str, db: Session):
    """This function creates an admin notification

    Args:
        admin_id (int): The admin's ID
        content (str): The notification content
        db (Session): The database session

    Returns:
        models.AdminNotification: The created notifcation notification obj
    """
    await selectors.get_admin_by_id(admin_id=admin_id, db=db)
    obj = models.AdminNotification(admin_id=admin_id, content=content)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
