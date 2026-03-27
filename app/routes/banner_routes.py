from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.db_connection import get_db
from app.schemas.banner import BannerOut, BannerCreate, BannerUpdate
from app.services import banner_service
from app.core.security import get_current_active_user

router = APIRouter(prefix="/banners", tags=["Banners"])


# PUBLIC ROUTES
@router.get("/public", response_model=List[BannerOut], status_code=status.HTTP_200_OK)
def get_public_banners(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    banner = banner_service.banner.get_active_for_website(db=db, skip=skip, limit=limit)
    return banner

# ADMIN ROUTES
@router.post("/", response_model=BannerOut, dependencies=[Depends(get_current_active_user)], status_code=201)
def create_banner(
        banner_in: BannerCreate,
        db: Session = Depends(get_db)
):
    new_banner = banner_service.banner.create(db=db, obj_in=banner_in)
    return new_banner

@router.get("/admin", response_model=List[BannerOut], dependencies=[Depends(get_current_active_user)], status_code=200)
def get_all_banners_admin(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    data = banner_service.banner.get_multi(db=db, skip=skip, limit=limit)
    return data

@router.patch("/{id}", response_model=BannerOut, dependencies=[Depends(get_current_active_user)], status_code=200)
def update_banner(
        id: uuid.UUID,
        banner_in: BannerUpdate,
        db: Session = Depends(get_db)
):
    banner = banner_service.banner.get(db=db, id=id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner_service.banner.update(db=db, db_obj=banner, obj_in=banner_in)


@router.delete("/{id}", dependencies=[Depends(get_current_active_user)], status_code=204)
def delete_banner(
        id: uuid.UUID,
        db: Session = Depends(get_db)
):
    banner = banner_service.banner.get(db=db, id=id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    banner_service.banner.remove(db=db, id=id)
    return {"message": "Banner successfully removed."}