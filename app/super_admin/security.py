from datetime import datetime, timedelta
from typing import Literal

import jwt
from fastapi import HTTPException, status

from app.config.settings import get_settings

settings = get_settings()


def generate_user_token(
    token_type: Literal["access", "refresh"], sub: str, expire_in: int
):
    """This function generates the user's jwt token

    Args:
        type (access, refresh): The type of token to generate
        sub (str): The subject of the token, typically the user's ID
        expire_in(int): The time in (minutes for access, hours for refresh) the token will expire
    Returns:
        str: The generated Token
    """
    if token_type not in ["access", "refresh"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Invalid Token Type",
        )
    iat = datetime.now()
    if token_type == "access":
        expire = datetime.now() + timedelta(minutes=expire_in)
    else:
        expire = datetime.now() + timedelta(hours=expire_in)

    data = {
        "type": token_type,
        "sub": sub,
        "iat": iat.timestamp(),
        "exp": expire.timestamp(),
        "iss": "shipnlogic.com",
    }
    return jwt.encode(
        payload=data,
        key=settings.SECRET_KEY,
        algorithm=settings.HASHING_ALGORITHM,
    )


def verify_user_refresh_token(token: str):
    """This function verifies the user's refresh token

    Args:
        token (str): The refresh token

    Returns:
        str: The user's ID
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=settings.HASHING_ALGORITHM,
        )
        sub: str = payload.get("sub")
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        return sub.split("-")[1]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )


def verify_user_access_token(token: str, raise_exception: bool = True):
    """This function verifies the user's access token

    Args:
        token (str): The access token

    Returns:
        str: The user's ID
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=settings.HASHING_ALGORITHM,
        )
        sub: str = payload.get("sub")
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        if sub is None:
            if raise_exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
                )
            return None
        return sub.split("-")[1]
    except jwt.ExpiredSignatureError:
        if raise_exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        return None
    except jwt.PyJWTError:
        if raise_exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        return None
