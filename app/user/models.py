from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.config.database import DBBase


class User(DBBase):
    """Database model for User"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_picture_url = Column(String, default="/default_profile.jpg", nullable=False)
    full_name = Column(String(50), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    exception_alert_email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class UserConfiguration(DBBase):
    """This is the base database schema for User configurations"""

    __tablename__ = "user_configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notification_email = Column(Boolean, default=True)
    notification_inapp = Column(Boolean, default=True)


class UserNotification(DBBase):
    """This is the base database schema for user notifications"""

    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

class UserRefreshToken(DBBase):
    """Database model for user refresh tokens"""

    __tablename__ = "user_refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String, nullable=False)