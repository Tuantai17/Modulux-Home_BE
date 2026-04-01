from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone
import json

from app.models.site import SiteSetting, Banner, CoreFeature, Video, Partner
from app.schemas.site import (
    SiteSettingCreate, SiteSettingUpdate,
    BannerCreate, BannerUpdate,
    CoreFeatureCreate, CoreFeatureUpdate,
    VideoCreate, VideoUpdate,
    PartnerCreate, PartnerUpdate,
    MenuConfigUpdate,
)

_now = lambda: datetime.now(timezone.utc)
MENU_CONFIG_KEY_PREFIX = "menu_config"
VIDEO_LOCATIONS = {"home", "faq", "both"}


def _default_menu_config(location: str = "header", locale: str = "en-US"):
    return {
        "location": location,
        "locale": locale,
        "cta_label": "Enquire Now",
        "cta_path": "/contact?type=project",
        "search_path": "/blogs",
        "items": [
            {"key": "about", "label": "About", "path": "/about", "order": 0, "is_active": True, "children": []},
            {
                "key": "what-we-do",
                "label": "What We Do",
                "path": "/why-modulux",
                "order": 1,
                "is_active": True,
                "children": [
                    {"key": "why-modulux", "label": "Why Modulux", "path": "/why-modulux", "order": 0, "is_active": True, "children": []},
                    {"key": "our-technology", "label": "Our Technology", "path": "/our-technology", "order": 1, "is_active": True, "children": []},
                    {"key": "technical-specification", "label": "Technical Specification", "path": "/technical-specification", "order": 2, "is_active": True, "children": []},
                    {"key": "our-process", "label": "Our Process", "path": "/our-process", "order": 3, "is_active": True, "children": []},
                    {"key": "projects", "label": "Projects", "path": "/projects", "order": 4, "is_active": True, "children": []},
                    {"key": "faqs", "label": "FAQs", "path": "/faqs", "order": 5, "is_active": True, "children": []},
                ],
            },
            {"key": "blog", "label": "Blog", "path": "/blogs", "order": 2, "is_active": True, "children": []},
            {"key": "contact", "label": "Contact", "path": "/contact?type=project", "order": 3, "is_active": True, "children": []},
        ],
    }


def _menu_setting_key(location: str, locale: str):
    return f"{MENU_CONFIG_KEY_PREFIX}:{location}:{locale}"


def _normalize_menu_item(item: dict, index: int = 0):
    children = item.get("children") or []
    return {
        "key": item.get("key") or f"item-{index + 1}",
        "label": item.get("label") or f"Menu {index + 1}",
        "path": item.get("path") or "/",
        "order": item.get("order", index),
        "is_active": bool(item.get("is_active", True)),
        "children": [_normalize_menu_item(child, child_index) for child_index, child in enumerate(children)],
    }


def _normalize_menu_config(data: dict | None, location: str = "header", locale: str = "en-US"):
    base = _default_menu_config(location=location, locale=locale)
    if not isinstance(data, dict):
        return base

    items = data.get("items") or base["items"]
    return {
        "location": data.get("location") or location,
        "locale": data.get("locale") or locale,
        "cta_label": data.get("cta_label") or base["cta_label"],
        "cta_path": data.get("cta_path") or base["cta_path"],
        "search_path": data.get("search_path") or base["search_path"],
        "items": [_normalize_menu_item(item, index) for index, item in enumerate(items)],
    }


def _normalize_video_location(raw_location: str | None):
    location = (raw_location or "home").strip().lower()
    if location not in VIDEO_LOCATIONS:
        return "home"
    return location


def get_menu_config(db: Session, location: str = "header", locale: str = "en-US"):
    setting = get_setting_by_key(db, _menu_setting_key(location, locale))
    if not setting:
        return _default_menu_config(location=location, locale=locale)

    try:
        raw_value = json.loads(setting.value)
    except (json.JSONDecodeError, TypeError):
        raw_value = None

    return _normalize_menu_config(raw_value, location=location, locale=locale)


def upsert_menu_config(db: Session, data: MenuConfigUpdate):
    payload = _normalize_menu_config(data.model_dump(), location=data.location, locale=data.locale)
    key_name = _menu_setting_key(payload["location"], payload["locale"])
    setting = get_setting_by_key(db, key_name)

    if setting:
        setting.value = json.dumps(payload, ensure_ascii=False)
        setting.description = f"Menu config for {payload['location']} ({payload['locale']})"
    else:
        setting = SiteSetting(
            key_name=key_name,
            value=json.dumps(payload, ensure_ascii=False),
            description=f"Menu config for {payload['location']} ({payload['locale']})",
        )
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return payload


# ─── SiteSetting ────────────────────────────────────────────────
def get_settings(db: Session):
    return db.query(SiteSetting).filter(SiteSetting.delete_at == None).all()


def get_setting(db: Session, setting_id: int):
    return db.query(SiteSetting).filter(SiteSetting.id == setting_id, SiteSetting.delete_at == None).first()


def get_setting_by_key(db: Session, key_name: str):
    return db.query(SiteSetting).filter(SiteSetting.key_name == key_name, SiteSetting.delete_at == None).first()


def create_setting(db: Session, data: SiteSettingCreate):
    obj = SiteSetting(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_setting(db: Session, setting_id: int, data: SiteSettingUpdate):
    obj = get_setting(db, setting_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_setting(db: Session, setting_id: int, deleted_by: int):
    obj = get_setting(db, setting_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── Banner ─────────────────────────────────────────────────────
def get_banners(db: Session):
    return db.query(Banner).filter(Banner.delete_at == None).order_by(Banner.display_order).all()


def get_banner(db: Session, banner_id: int):
    return db.query(Banner).filter(Banner.id == banner_id, Banner.delete_at == None).first()


def create_banner(db: Session, data: BannerCreate):
    obj = Banner(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_banner(db: Session, banner_id: int, data: BannerUpdate):
    obj = get_banner(db, banner_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_banner(db: Session, banner_id: int, deleted_by: int):
    obj = get_banner(db, banner_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── CoreFeature ────────────────────────────────────────────────
def get_core_features(db: Session):
    return db.query(CoreFeature).filter(CoreFeature.delete_at == None).order_by(CoreFeature.display_order).all()


def get_core_feature(db: Session, feature_id: int):
    return db.query(CoreFeature).filter(CoreFeature.id == feature_id, CoreFeature.delete_at == None).first()


def create_core_feature(db: Session, data: CoreFeatureCreate):
    obj = CoreFeature(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_core_feature(db: Session, feature_id: int, data: CoreFeatureUpdate):
    obj = get_core_feature(db, feature_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_core_feature(db: Session, feature_id: int, deleted_by: int):
    obj = get_core_feature(db, feature_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── Video ──────────────────────────────────────────────────────
def get_videos(db: Session, location: str = "home"):
    normalized_location = _normalize_video_location(location)
    location_filters = [Video.location == normalized_location]
    if normalized_location in {"home", "faq"}:
        location_filters.append(Video.location == "both")

    return (
        db.query(Video)
        .filter(
            Video.delete_at == None,
            Video.is_active == True,
            or_(*location_filters),
        )
        .order_by(Video.display_order.asc().nullslast(), Video.id.asc())
        .all()
    )


def get_videos_for_admin(db: Session, location: str | None = None):
    query = db.query(Video).filter(Video.delete_at == None)
    if location:
        query = query.filter(Video.location == _normalize_video_location(location))

    return query.order_by(Video.location.asc(), Video.display_order.asc().nullslast(), Video.id.asc()).all()


def get_video(db: Session, video_id: int):
    return db.query(Video).filter(Video.id == video_id, Video.delete_at == None).first()


def create_video(db: Session, data: VideoCreate):
    payload = data.model_dump()
    payload["location"] = _normalize_video_location(payload.get("location"))
    if not payload.get("thumbnail_label"):
        payload["thumbnail_label"] = payload.get("title") or "Video"
    if not payload.get("poster_url"):
        payload["poster_url"] = payload.get("thumbnail_url")

    obj = Video(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_video(db: Session, video_id: int, data: VideoUpdate):
    obj = get_video(db, video_id)
    if obj:
        payload = data.model_dump(exclude_none=True)
        if "location" in payload:
            payload["location"] = _normalize_video_location(payload.get("location"))
        for k, v in payload.items():
            setattr(obj, k, v)

        if "thumbnail_label" in payload and not obj.thumbnail_label:
            obj.thumbnail_label = obj.title or "Video"

        if "poster_url" in payload and not obj.poster_url:
            obj.poster_url = obj.thumbnail_url

        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_video(db: Session, video_id: int, deleted_by: int):
    obj = get_video(db, video_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── Partner ────────────────────────────────────────────────────
def get_partners(db: Session):
    return db.query(Partner).filter(Partner.delete_at == None).order_by(Partner.display_order).all()


def get_partner(db: Session, partner_id: int):
    return db.query(Partner).filter(Partner.id == partner_id, Partner.delete_at == None).first()


def create_partner(db: Session, data: PartnerCreate):
    obj = Partner(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_partner(db: Session, partner_id: int, data: PartnerUpdate):
    obj = get_partner(db, partner_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_partner(db: Session, partner_id: int, deleted_by: int):
    obj = get_partner(db, partner_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj
