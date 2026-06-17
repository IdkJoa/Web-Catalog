import logging
import uuid

from fastapi import APIRouter
from fastapi import Depends, status, HTTPException
from typing import List

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from sqlalchemy.orm import Session
from app.schemas.site_settings import SiteSettingsCreate, SiteSettingsUpdate, SiteSettingsOut
from app.services.site_settings_service import site_settings_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/site_settings", tags=["Site Settings"])

@router.get("/site-settings", response_model=List[SiteSettingsOut], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)])
def get_site_settings(
        #id: uuid.UUID,
        skip: int = 0, limit: int = 10,
        db: Session = Depends(get_db),
):
    logger.debug(f"Fetching site settings: skip={skip}, limit={limit}")
    data = site_settings_service.get_all_no_filtered(db=db, skip=skip, limit=limit)
    return data

@router.post("/site-settings", response_model=SiteSettingsOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_user)])
def create_site_settings(
    setting_in: SiteSettingsCreate,
    db: Session = Depends(get_db)
):
    logger.info("Creating new site settings")
    new_setting = site_settings_service.create(db=db, obj_in=setting_in)
    logger.info(f"Site settings created with id: {getattr(new_setting, 'id', 'N/A')}")
    return new_setting


# 1. Added /{id} to the path so FastAPI knows where to map the UUID
@router.put("/site-settings/{id}", response_model=SiteSettingsOut, status_code=status.HTTP_202_ACCEPTED,
            dependencies=[Depends(get_current_active_user)])
def update_site_settings(
        id: uuid.UUID,
        setting: SiteSettingsUpdate,
        db: Session = Depends(get_db),
):
    logger.info(f"Updating site settings with id: {id}")
    setting_exist = site_settings_service.get(db=db, id=id)

    if setting_exist is None:
        logger.warning(f"Update failed: Site settings {id} not found")
        raise HTTPException(status_code=404, detail="Site settings not found.")

    setting_update = site_settings_service.update(db=db, obj_in=setting, db_obj=setting_exist)
    logger.info(f"Site settings {id} updated successfully")
    return setting_update

@router.delete("/site-settings{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
def delete_site_settings(
        id_in: uuid.UUID ,
        db: Session = Depends(get_db),
):
    logger.info(f"Deleting site settings with id: {id_in}")
    setting_exist = site_settings_service.get(db=db, id=id_in)
    if not setting_exist:
        logger.warning(f"Delete failed: Site settings {id_in} not found")
        raise HTTPException(status_code=404, detail="Site settings not found.")
        
    site_settings_service.delete(db=db, id=id_in)
    logger.info(f"Site settings {id_in} deleted successfully")
    return {"message": "Site settings deleted successfully"}



