import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.db_connection import get_db
from app.schemas.banner import BannerOut, BannerCreate, BannerUpdate
from app.services import banner_service
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/banners", tags=["Banners"])


# PUBLIC ROUTES
@router.get("/public", response_model=List[BannerOut], status_code=status.HTTP_200_OK)
def get_public_banners(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.debug(f"Fetching public banners: skip={skip}, limit={limit}")
    banner = banner_service.banner.get_active_for_website(db=db, skip=skip, limit=limit)
    return banner

# ADMIN ROUTES
@router.post("/", response_model=BannerOut, dependencies=[Depends(get_current_active_user)], status_code=201)
def create_banner(
        banner_in: BannerCreate,
        db: Session = Depends(get_db)
):
    logger.info(f"Creating new banner: {banner_in.title}")
    new_banner = banner_service.banner.create(db=db, obj_in=banner_in)
    logger.info(f"Banner created with id: {new_banner.id}")
    return new_banner

@router.get("/admin", response_model=List[BannerOut], dependencies=[Depends(get_current_active_user)], status_code=200)
def get_all_banners_admin(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    logger.debug(f"Admin fetching all banners: skip={skip}, limit={limit}")
    data = banner_service.banner.get_multi(db=db, skip=skip, limit=limit)
    return data

@router.patch("/{id}", response_model=BannerOut, dependencies=[Depends(get_current_active_user)], status_code=200)
def update_banner(
        id: uuid.UUID,
        banner_in: BannerUpdate,
        db: Session = Depends(get_db)
):
    logger.info(f"Updating banner with id: {id}")
    banner = banner_service.banner.get(db=db, id=id)
    if not banner:
        logger.warning(f"Update failed: Banner {id} not found")
        raise HTTPException(status_code=404, detail="Banner not found")
    updated_banner = banner_service.banner.update(db=db, db_obj=banner, obj_in=banner_in)
    logger.info(f"Banner {id} updated successfully")
    return updated_banner


@router.delete("/{id}", dependencies=[Depends(get_current_active_user)], status_code=204)
def delete_banner(
        id: uuid.UUID,
        db: Session = Depends(get_db)
):
    logger.info(f"Deleting banner with id: {id}")
    banner = banner_service.banner.get(db=db, id=id)
    if not banner:
        logger.warning(f"Delete failed: Banner {id} not found")
        raise HTTPException(status_code=404, detail="Banner not found")

    banner_service.banner.delete(db=db, id=id)
    logger.info(f"Banner {id} deleted successfully")
    return {"message": "Banner successfully removed."}