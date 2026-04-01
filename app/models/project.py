from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    thumbnail_url = Column(String, nullable=True)
    installation_time = Column(String, nullable=True)
    location = Column(String, nullable=True)
    area_sqft = Column(Integer, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    stories = Column(Integer, nullable=True)
    kitchens = Column(Integer, nullable=True)
    floor_plan_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    features = Column(JSON, nullable=True)
    finishing_options = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False)
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)

    images = relationship("ProjectImage", back_populates="project", lazy="select")


class ProjectImage(Base):
    __tablename__ = "project_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    image_url = Column(String, nullable=False)
    display_order = Column(Integer, nullable=True)
    is_hero = Column(Boolean, default=False)
    is_floor_plan = Column(Boolean, default=False)
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)

    project = relationship("Project", back_populates="images")
