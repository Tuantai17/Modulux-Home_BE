from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.crud.crud_site import get_menu_config, upsert_menu_config
from app.schemas.site import MenuConfigOut, MenuConfigUpdate, PublicMenuOut

router = APIRouter(prefix="/site/menu", tags=["Navigation"])


@router.get("", response_model=PublicMenuOut)
def read_public_menu(
    location: str = "header",
    locale: str = "en-US",
    db: Session = Depends(get_db),
):
    config = get_menu_config(db, location=location, locale=locale)
    return {
        "location": config["location"],
        "locale": config["locale"],
        "cta": {
            "label": config["cta_label"],
            "path": config["cta_path"],
        },
        "search": {
            "path": config["search_path"],
        },
        "items": config["items"],
    }


@router.get("/config", response_model=MenuConfigOut)
def read_menu_config(
    location: str = "header",
    locale: str = "en-US",
    db: Session = Depends(get_db),
):
    return get_menu_config(db, location=location, locale=locale)


@router.put("", response_model=MenuConfigOut)
def save_menu_config(
    payload: MenuConfigUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return upsert_menu_config(db, payload)
