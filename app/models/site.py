from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from app.db.session import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key_name = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=True)
    subtitle = Column(String, nullable=True)
    media_url = Column(String, nullable=False)
    button_text = Column(String, nullable=True)
    button_link = Column(String, nullable=True)
    display_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)


class CoreFeature(Base):
    __tablename__ = "core_features"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    display_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location = Column(String, nullable=False, default="home")
    title = Column(String, nullable=True)
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    thumbnail_label = Column(String, nullable=True)
    display_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=False)
    display_order = Column(Integer, nullable=True)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)
