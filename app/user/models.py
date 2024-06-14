from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

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
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class UserPasswordResetToken(DBBase):
    """Database model for user password reset tokens"""

    __tablename__ = "user_password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String, unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class NewsLetter(DBBase):
    """Database model for newsletter subscribers"""

    __tablename__ = "newsletter"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class Company(DBBase):
    """Database model for company"""

    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    registration_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    tax_identification_number = Column(String, unique=True, nullable=False)
    license_image_url = Column(String, default="/default_license.jpg", nullable=False)
    permit_image_url = Column(String, default="/default_permit.jpg", nullable=False)
    is_verified = Column(Boolean, default=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


class Support(DBBase):
    """Database model for support"""

    __tablename__ = "support"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    email = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    upload_file_url = Column(String, default="/upload_file.png", nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
