"""This module contains common dependencies used in the application"""

from app.common.types import PaginationParamsType
from app.config.database import SessionLocal


def get_db():
    """This function starts a db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def pagination_params(page: int = 1, size: int = 10):
    """Helper Dependency for pagination"""
    return PaginationParamsType(page=page, size=size)
