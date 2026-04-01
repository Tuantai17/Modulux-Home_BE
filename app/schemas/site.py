from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


# ─── SiteSetting ───────────────────────────────────────────────
class SiteSettingCreate(BaseModel):
    key_name: str
    value: str
    description: Optional[str] = None


class SiteSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class SiteSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key_name: str
    value: str
    description: Optional[str] = None


# ─── Menu Config ────────────────────────────────────────────────
class MenuItemBase(BaseModel):
    key: str
    label: str
    path: str
    order: int = 0
    is_active: bool = True


class MenuItem(MenuItemBase):
    children: list['MenuItem'] = Field(default_factory=list)


class MenuConfigBase(BaseModel):
    location: str = 'header'
    locale: str = 'en-US'
    cta_label: str = 'Enquire Now'
    cta_path: str = '/contact?type=project'
    search_path: str = '/blogs'
    items: list[MenuItem] = Field(default_factory=list)


class MenuConfigUpdate(MenuConfigBase):
    pass


class MenuConfigOut(MenuConfigBase):
    pass


class PublicMenuAction(BaseModel):
    label: str
    path: str


class PublicMenuSearch(BaseModel):
    path: str


class PublicMenuOut(BaseModel):
    location: str
    locale: str
    cta: PublicMenuAction
    search: PublicMenuSearch
    items: list[MenuItem] = Field(default_factory=list)


# ─── Banner ──────────────────────────────────────────────────────
class BannerCreate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    media_url: str
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = True


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    media_url: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str] = None
    subtitle: Optional[str] = None
    media_url: str
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    display_order: Optional[int] = None
    is_active: bool


# ─── CoreFeature ────────────────────────────────────────────────
class CoreFeatureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = True


class CoreFeatureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CoreFeatureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: bool


# ─── Video ──────────────────────────────────────────────────────
class VideoCreate(BaseModel):
    location: Optional[str] = "home"
    title: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    poster_url: Optional[str] = None
    thumbnail_label: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = True


class VideoUpdate(BaseModel):
    location: Optional[str] = None
    title: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    poster_url: Optional[str] = None
    thumbnail_label: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location: str = "home"
    title: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    poster_url: Optional[str] = None
    thumbnail_label: Optional[str] = None
    display_order: Optional[int] = None
    is_active: bool


# ─── Partner ────────────────────────────────────────────────────
class PartnerCreate(BaseModel):
    name: str
    logo_url: str
    display_order: Optional[int] = None


class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    display_order: Optional[int] = None


class PartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    logo_url: str
    display_order: Optional[int] = None
