from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.security import hash_password, verify_password
from app.user import models, selectors
from app.user.schemas import base_schemas, create_schemas, edit_schemas


async def create_user(data: create_schemas.UserCreate, db: Session):
    """This function creates a new user

    Args:
        data (create_schemas.UserCreate): The user's data
        db (Session): The database session

    Raises:
        HTTPException[400]: User with email exists

    Returns:
        models.User: The created user obj
    """
    # Validate unique email
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user with email {data.email} exists",
        )

    obj = models.User(**data.model_dump())
    obj.password = hash_password(raw=data.password)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def create_user_configuration(user_id: int, db: Session):
    """This function creates the user's configuration obj

    Args:
        user_id (int): The user's ID
        db (Session): The database session

    Returns:
        models.UserConfiguration: The created user configuration obj
    """
    await selectors.get_user_by_id(user_id=user_id, db=db)
    if db.query(models.UserConfiguration).filter_by(user_id=user_id).first():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"user configuration for user {user_id} already exists",
        )
    obj = models.UserConfiguration(user_id=user_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def create_user_notification(user_id: int, content: str, db: Session):
    """This function creates a user notification

    Args:
        user_id (int): The user's ID
        content (str): The notification content
        db (Session): The database session

    Returns:
        models.UserNotification: The created user notification obj
    """
    await selectors.get_user_by_id(user_id=user_id, db=db)
    obj = models.UserNotification(user_id=user_id, content=content)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def login_user(
    data: base_schemas.UserLoginCredential,
    db: Session,
    raise_exception: bool = True,
):
    """This function logs in a user and updates their last_login

    Args:
        data (base_schemas.UserLoginCredential): The user's login credentials
        db (Session): The database session
        raise_exception(bool, default=True): Indicates whether to raise an exception or not

    Raises:
        HTTPException[401]: Invalid login credentials

    Returns:
        (models.User, None): The user's model obj
    """
    user = await selectors.get_user_by_email(
        email=data.email, db=db, raise_exception=False
    )
    if not user:
        if raise_exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            )
        return None
    if verify_password(plain_password=data.password, hashed_password=user.password):
        user.last_login = datetime.now()
        db.commit()
        db.refresh(user)
        return user
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
        )
    return None


async def create_user_refresh_token(user_id: int, token: str, db: Session):
    """This function creates a user refresh token

    Args:
        user_id (int): The user's ID
        token(str): The access token
        db (Session): The database session

    Returns:
        models.UserRefreshToken: The created user refresh token obj
    """
    await selectors.get_user_by_id(user_id=user_id, db=db)
    obj = models.UserRefreshToken(user_id=user_id, token=token)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def edit_user(user_id: int, data: edit_schemas.UserEdit, db: Session):
    """This function edits a user's details

    Args:
        user_id (int): The user's ID
        data (edit_schemas.UserEdit): The user's data
        db (Session): The database session

    Returns:
        models.User: The edited user obj
    """
    obj = await selectors.get_user_by_id(user_id=user_id, db=db)
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


async def create_newsletter_subscriber(email: str, db: Session):
    """This function creates a newsletter subscription

    Args:
        email (str): The subscriber's email
        db (Session): The database session

    Returns:
        models.Newsletter: The created newsletter subscription obj
    """
    if db.query(models.NewsLetter).filter_by(email=email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"email {email} already subscribed",
        )
    obj = models.NewsLetter(email=email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def create_company(user_id: int, data: create_schemas.CompanyCreate, db: Session):
    """This function creates a new company

    Args:
        data (create_schemas.CompanyCreate): The company's data
        db (Session): The database session

    Raises:
        HTTPException[400]: Company with email exists

    Returns:
        models.Company: The created company obj
    """
    # Validate unique email
    if db.query(models.Company).filter_by(email=data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"company with email {data.email} exists",
        )

    obj = models.Company(**data.model_dump())
    obj.user_id = user_id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
