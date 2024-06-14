from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum, ForeignKey

from app.config.database import DBBase


class Admin(DBBase):
    """Database model for Admin"""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_picture_url = Column(String, default="/default_profile.jpg", nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    added_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    gender = Column(Enum("MALE", "FEMALE", "OTHER", name="gender_enum"), nullable=False)
    permission = Column(Enum("SUPER_ADMIN", "ADMIN", name="admin_enum"), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class AdminConfiguration(DBBase):
    """This is the base database schema for Admin configurations"""

    __tablename__ = "admin_configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False
    )
    notification_email = Column(Boolean, default=True)
    notification_inapp = Column(Boolean, default=True)


class AdminNotification(DBBase):
    """This is the base database schema for admin notifications"""

    __tablename__ = "admin_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
