from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ─── Contact ─────────────────────────────────────────────────────
class ContactCreate(BaseModel):
    enquiry_type: str = "general"
    first_name: str
    last_name: str
    email: str
    country_code: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    message: Optional[str] = None

    # Project Enquiry fields
    building_type: Optional[str] = None
    living_units: Optional[str] = None
    area: Optional[str] = None
    arrange_tour: bool = False
    preferred_day: Optional[str] = None
    preferred_time: Optional[str] = None
    file_url: Optional[str] = None

    # General Enquiry fields
    get_brochure: bool = False


class ContactUpdate(BaseModel):
    status: Optional[str] = None


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enquiry_type: Optional[str] = "general"
    first_name: str
    last_name: str
    email: str
    country_code: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    message: Optional[str] = None

    building_type: Optional[str] = None
    living_units: Optional[str] = None
    area: Optional[str] = None
    arrange_tour: Optional[bool] = False
    preferred_day: Optional[str] = None
    preferred_time: Optional[str] = None
    file_url: Optional[str] = None

    get_brochure: Optional[bool] = False

    status: str
    created_at: Optional[datetime] = None


# ─── Subscriber ──────────────────────────────────────────────────
class SubscriberCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    is_active: bool
    created_at: Optional[datetime] = None
