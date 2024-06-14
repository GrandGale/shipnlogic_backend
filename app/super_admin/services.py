from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.security import hash_password, verify_password
from app.super_admin import models, selectors
from app.super_admin.schemas import base_schemas, create_schemas, edit_schemas


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


async def login_admin(
    data: base_schemas.AdminLoginCredential,
    db: Session,
    raise_exception: bool = True,
):
    """This function logs in an admin and updates their last_login

    Args:
        data (base_schemas.AdminLoginCredential): The admin's login credentials
        db (Session): The database session
        raise_exception(bool, default=True): Indicates whether to raise an exception or not

    Raises:
        HTTPException[401]: Invalid login credentials

    Returns:
        (models.Admin, None): The admin's model obj
    """
    admin = await selectors.get_admin_by_email(
        email=data.email, db=db, raise_exception=False
    )
    if not admin:
        if raise_exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            )
        return None
    if verify_password(plain_password=data.password, hashed_password=admin.password):
        admin.last_login = datetime.now()
        db.commit()
        db.refresh(admin)
        return admin
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
        )
    return None


async def create_admin_refresh_token(admin_id: int, token: str, db: Session):
    """This function creates an admin refresh token

    Args:
        admin_id (int): The admin's ID
        token(str): The access token
        db (Session): The database session

    Returns:
        models.AdminRefreshToken: The created admin refresh token obj
    """
    await selectors.get_admin_by_id(admin_id=admin_id, db=db)
    obj = models.AdminRefreshToken(admin_id=admin_id, token=token)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def edit_admin(admin_id: int, data: edit_schemas.AdminEdit, db: Session):
    """This function edits an admin's details

    Args:
        admin_id (int): The admin's ID
        data (edit_schemas.AdminEdit): The admin's data
        db (Session): The database session

    Returns:
        models.Admin: The edited admin obj
    """
    obj = await selectors.get_admin_by_id(admin_id=admin_id, db=db)
    data = data.model_dump(exclude_unset=True)
    if data == {}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update",
        )
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj
