from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
from app.db.session import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Phân loại form
    enquiry_type = Column(String, default="general")
    # Giá trị: 'home_general', 'general', 'project'

    # Thông tin chung (cả 3 form)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    country_code = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)
    message = Column(Text, nullable=True)

    # Chỉ cho Project Enquiry
    building_type = Column(String, nullable=True)
    living_units = Column(String, nullable=True)
    area = Column(String, nullable=True)
    arrange_tour = Column(Boolean, default=False)
    preferred_day = Column(String, nullable=True)
    preferred_time = Column(String, nullable=True)
    file_url = Column(String, nullable=True)

    # Chỉ cho General Enquiry
    get_brochure = Column(Boolean, default=False)

    # Quản lý
    status = Column(String, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delete_at = Column(DateTime(timezone=True), nullable=True)
    delete_by = Column(Integer, nullable=True)
